"""Stage 2: Self-RAG retrieval decision over the Orbitra knowledge base.

Flow: question -> decide_retrieval -> (yes) retrieve -> generate -> answer
                                   -> (no)  generate_direct      -> answer
"""
from pathlib import Path
from typing import Literal, TypedDict

import yaml
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

load_dotenv()

DOCS_DIR = Path("documents")
MODELS_DIR = "models"
CHROMA_DIR = "chroma_db"
COLLECTION = "orbitra_kb"

# load the documents and parse the YAML header functions
def parse_markdown(path: Path) -> Document:
    """Read one .md file and turn its YAML front-matter into metadata."""
    text = path.read_text(encoding="utf-8")
    metadata = {"source": str(path)}

    if text.startswith("---"):
        _, front_matter, text = text.split("---", 2)
        try:
            header = yaml.safe_load(front_matter)
        except yaml.YAMLError:
            # e.g. HR-POSH-001 has an unquoted ": " inside a value, so read plain "key: value" lines
            lines = [line.split(":", 1) for line in front_matter.strip().splitlines() if ":" in line]
            header = {k.strip(): v.strip() for k, v in lines}
        for key, value in header.items():
            if value is None:
                continue
            # Chroma only stores str/int/float/bool, so flatten lists and dates
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            elif not isinstance(value, (str, int, float, bool)):
                value = str(value)
            metadata[key] = value

    return Document(page_content=text.strip(), metadata=metadata)


def load_documents() -> list[Document]:
    return [parse_markdown(p) for p in sorted(DOCS_DIR.rglob("*.md"))]

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

# ONNX model, downloaded into models/ on the first run (bge vectors come out normalized).
# batch_size: default is 256, which needs >1.5 GB RAM for these chunks and froze the laptop.
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5", cache_dir=MODELS_DIR, batch_size=16)


# embeddings and the vectorstore (build once, and then load)
def get_vectorstore() -> Chroma:
    """Load the saved Chroma DB, or (re)build it if it is missing or incomplete."""
    vectorstore = Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    chunks = splitter.split_documents(load_documents())

    # fewer chunks than expected means first run, or an earlier build crashed halfway
    stored = len(vectorstore.get(include=[])["ids"])
    if stored == len(chunks):
        return vectorstore
    if stored:
        print(f"Vectorstore is incomplete ({stored}/{len(chunks)} chunks), rebuilding...")
        vectorstore.reset_collection()

    print(f"Building vectorstore from {len(chunks)} chunks...")
    step = embeddings.batch_size
    for i in range(0, len(chunks), step):
        vectorstore.add_documents(chunks[i:i + step])
        print(f"\r  embedded {min(i + step, len(chunks))}/{len(chunks)} chunks", end="", flush=True)
    print()
    return vectorstore


vectorstore = get_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# llm and prompt
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are OrbitBot, an internal assistant for Orbitra Technologies employees. "
     "Answer the question using only the context below. If the context does not "
     "contain the answer, say you don't know. If the answer depends on details the "
     "user did not give (location, level, etc.), list the options from the context "
     "and ask which applies. Cite the doc_id of every source you use, like "
     "[HR-LV-001].\n\nContext:\n{context}"),
    ("human", "{question}"),
])

def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(f"[{d.metadata.get('doc_id', '?')}] {d.page_content}" for d in docs)


# retrieval decision (Self-RAG's "Retrieve" step), returned as a Pydantic object
class RetrievalDecision(BaseModel):
    """Decide whether the question needs Orbitra's knowledge base."""
    should_retrieve: bool = Field(description="True if answering needs Orbitra's internal documents "
        "(policies, processes, people, products, company facts); False for greetings, small talk, "
        "or general knowledge unrelated to Orbitra.")
    reason: str = Field(description="One short sentence explaining the decision.")


decide_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You decide whether a question to OrbitBot, the internal assistant of Orbitra Technologies, "
     "needs a search of the company knowledge base (HR, IT, security, finance, admin, legal, "
     "engineering, product and sales documents). Retrieve for anything about Orbitra or how things "
     "work there, even if it sounds general (e.g. 'how do I reset my password?'). Do not retrieve "
     "for greetings, thanks, small talk, or general knowledge unrelated to Orbitra. When unsure, retrieve."),
    ("human", "{question}"),
])
decider = decide_prompt | llm.with_structured_output(RetrievalDecision)

direct_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are OrbitBot, an internal assistant for Orbitra Technologies employees. Answer briefly. "
     "This question was judged not to need company documents, so do not state any Orbitra-specific "
     "facts or policies; if the user needs those, suggest they ask about them directly."),
    ("human", "{question}"),
])


# the graph(state,nodes,edges)
class GraphState(TypedDict):
    question: str
    should_retrieve: bool
    retrieval_reason: str
    documents: list[Document]
    answer: str


def decide_retrieval(state: GraphState) -> dict:
    decision = decider.invoke({"question": state["question"]})
    return {"should_retrieve": decision.should_retrieve, "retrieval_reason": decision.reason}


# router, not a node: only reads the state and names the next node
def route_after_decision(state: GraphState) -> Literal["retrieve", "generate_direct"]:
    return "retrieve" if state["should_retrieve"] else "generate_direct"


def retrieve(state: GraphState) -> dict:
    docs = retriever.invoke(state["question"])
    return {"documents": docs}


def generate(state: GraphState) -> dict:
    chain = prompt | llm
    response = chain.invoke({
        "context": format_docs(state["documents"]),
        "question": state["question"],
    })
    return {"answer": response.content}


def generate_direct(state: GraphState) -> dict:
    response = (direct_prompt | llm).invoke({"question": state["question"]})
    return {"answer": response.content}


builder = StateGraph(GraphState)
builder.add_node("decide_retrieval", decide_retrieval)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("generate_direct", generate_direct)
builder.add_edge(START, "decide_retrieval")
builder.add_conditional_edges("decide_retrieval", route_after_decision)
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)
builder.add_edge("generate_direct", END)
app = builder.compile()


def ask(question: str):
    for step in app.stream({"question": question}, stream_mode="updates"):
        for node, update in step.items():
            print(f"--- {node} ---")
            if node == "decide_retrieval":
                print(f"  retrieve={update['should_retrieve']}  ({update['retrieval_reason']})")
            elif node == "retrieve":
                for d in update["documents"]:
                    print(f"  [{d.metadata.get('doc_id')}] status={d.metadata.get('status')}  "
                          f"{d.page_content[:80]!r}")
            else:
                print(update["answer"])


def main():
    print("OrbitBot is ready. Ask a question, or type 'exit' to quit.")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):  # Ctrl+D / Ctrl+C
            break
        if question.lower() in {"exit", "quit"}:
            break
        if question:
            ask(question)
    print("\nBye!")


if __name__ == "__main__":
    main()
