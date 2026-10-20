"""Stage 5: Self-RAG retrieval decision + document grading + support check + usefulness check
with query rewriting, over the Orbitra knowledge base.

Flow: question -> decide_retrieval -> (yes) retrieve -> grade_documents
                                   -> (no)  generate_direct -> answer
      grade_documents -> (some relevant) generate -> check_support
                      -> (none relevant, rewrite left) rewrite_query -> retrieve
                      -> (none relevant, no rewrite left) no_relevant_docs -> answer
      check_support -> (fully supported) check_useful
                    -> (not supported, retry left) revise_answer -> check_support
                    -> (not supported, no retry left) flag_unsupported -> answer
      check_useful -> (useful, or no rewrite left) answer
                   -> (not useful, rewrite left) rewrite_query -> retrieve
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
# max_retries: on a 429 (free tier is 8000 tokens/min) the client waits as Groq says, then retries
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, max_retries=6)
# yes/no judgments don't need deep thinking; fewer reasoning tokens = fewer rate-limit hits.
# set on the model itself: llm.bind(reasoning_effort=...) is dropped by with_structured_output
judge_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0, max_retries=6, reasoning_effort="low")

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
decider = decide_prompt | judge_llm.with_structured_output(RetrievalDecision)

direct_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are OrbitBot, an internal assistant for Orbitra Technologies employees. Answer briefly. "
     "This question was judged not to need company documents, so do not state any Orbitra-specific "
     "facts or policies; if the user needs those, suggest they ask about them directly."),
    ("human", "{question}"),
])


# document grading (Self-RAG's "IsRel" step), one grade per retrieved chunk
class DocGrade(BaseModel):
    """Relevance grade for one retrieved chunk."""
    is_relevant: bool = Field(description="True if the chunk contains information that helps answer "
        "the question; False if it is off-topic, superseded, or for a different region or group "
        "than the question asks about.")
    reason: str = Field(description="One short sentence explaining the grade.")


grade_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You grade whether a chunk from Orbitra's knowledge base is relevant to an employee's question. "
     "Use the chunk's metadata: a chunk with status 'superseded' is never relevant, because a newer "
     "version exists. A chunk whose applies_to clearly excludes the region or group the question is "
     "about is not relevant. If the question names no region, any region can be relevant. Otherwise "
     "be lenient: the chunk only needs to contain part of the answer."),
    ("human",
     "Question: {question}\n\nChunk metadata: doc_id={doc_id}, title={title}, status={status}, "
     "applies_to={applies_to}\n\nChunk:\n{chunk}"),
])
grader = grade_prompt | judge_llm.with_structured_output(DocGrade)


# support check (Self-RAG's "IsSup" step): is the answer grounded in the chunks?
class SupportGrade(BaseModel):
    """How well the retrieved chunks support the generated answer."""
    support: Literal["fully", "partially", "none"] = Field(description="'fully' if every factual "
        "claim in the answer is stated in, or directly calculated from, the chunks; 'partially' if "
        "some claims are not; 'none' if the answer is mostly unsupported.")
    unsupported_claims: list[str] = Field(description="Each claim not backed by the chunks; "
        "empty if fully supported.")


support_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You check whether an answer from OrbitBot is grounded in the retrieved chunks from Orbitra's "
     "knowledge base. A claim is supported if a chunk states it, if the user stated it in their "
     "question (e.g. their own salary, dates or counts), or if it is a direct calculation or "
     "rewording of those. Saying 'I don't know', asking the user a clarifying question, and "
     "citations like [HR-LV-001] are not claims. Anything else, such as numbers, names, rules or "
     "steps not found in the chunks or the question, is unsupported.\n\nChunks:\n{context}"),
    ("human", "Question: {question}\n\nAnswer to check:\n{answer}"),
])
support_checker = support_prompt | judge_llm.with_structured_output(SupportGrade)

# used when the support check fails: edit the previous answer instead of starting over
revise_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are OrbitBot, an internal assistant for Orbitra Technologies employees. Your previous "
     "answer contained claims that the context does not support. Remove or correct only those "
     "claims and keep the rest of the answer as it was. Do not add any new details, even ones that "
     "seem helpful. Keep the doc_id citations like [HR-LV-001].\n\nContext:\n{context}"),
    ("human", "Question: {question}\n\nPrevious answer:\n{answer}\n\nUnsupported claims:\n{claims}"),
])

MAX_GENERATIONS = 2   # first answer + one revision


# usefulness check (Self-RAG's "IsUse" step): does the answer address the question?
class UsefulnessGrade(BaseModel):
    """Whether the answer actually addresses the user's question."""
    is_useful: bool = Field(description="True if the answer gives the user what they asked for, or asks "
        "a clarifying question with the options from the documents; False if it says the information "
        "is not available or answers a different question.")
    reason: str = Field(description="One short sentence explaining the grade.")


useful_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You check whether OrbitBot's answer is useful to the employee who asked the question. Judge only "
     "whether it addresses what was asked, not whether it is correct; correctness was already checked."),
    ("human", "Question: {question}\n\nAnswer:\n{answer}"),
])
usefulness_checker = useful_prompt | judge_llm.with_structured_output(UsefulnessGrade)

# query rewriting: a new search query for retrieve only; grading and generation keep the original question
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You rewrite an employee's question into a search query for Orbitra's internal knowledge base "
     "(HR, IT, finance, admin, legal, engineering policies). The search is semantic, over policy "
     "documents. Never copy the user's own amounts, salaries, counts or dates into the query, and "
     "drop any calculation; keep the region/location; use the words a "
     "policy document would use (e.g. 'entitlement', 'leave types', 'notice period'). "
     "Return only the query."),
    ("human", "Question: {question}\n\nThis search query did not find the answer: {previous_query}"),
])
rewriter = rewrite_prompt | judge_llm

MAX_REWRITES = 1


# the graph(state,nodes,edges)
class GraphState(TypedDict):
    question: str
    should_retrieve: bool
    retrieval_reason: str
    documents: list[Document]
    doc_grades: list[dict]
    answer: str
    generation_attempts: int
    support: str
    unsupported_claims: list[str]
    search_query: str  # what retrieve searches for; the original question until a rewrite
    rewrite_count: int
    is_useful: bool
    usefulness_reason: str


def decide_retrieval(state: GraphState) -> dict:
    decision = decider.invoke({"question": state["question"]})
    return {"should_retrieve": decision.should_retrieve, "retrieval_reason": decision.reason}


# router, not a node: only reads the state and names the next node
def route_after_decision(state: GraphState) -> Literal["retrieve", "generate_direct"]:
    return "retrieve" if state["should_retrieve"] else "generate_direct"


def retrieve(state: GraphState) -> dict:
    docs = retriever.invoke(state.get("search_query") or state["question"])
    return {"documents": docs}


def grade_documents(state: GraphState) -> dict:
    docs = state["documents"]
    grades = grader.batch([
        {"question": state["question"], "chunk": d.page_content,
         **{k: d.metadata.get(k, "?") for k in ("doc_id", "title", "status", "applies_to")}}
        for d in docs
    ])  # one LLM call per chunk, sent in parallel
    # no reducer on "documents", so this filtered list replaces the one retrieve wrote
    return {
        "documents": [d for d, g in zip(docs, grades) if g.is_relevant],
        "doc_grades": [{"doc_id": d.metadata.get("doc_id"), "relevant": g.is_relevant, "reason": g.reason}
                       for d, g in zip(docs, grades)],
    }


def route_after_grading(state: GraphState) -> Literal["generate", "rewrite_query", "no_relevant_docs"]:
    if state["documents"]:
        return "generate"
    if state.get("rewrite_count", 0) < MAX_REWRITES:
        return "rewrite_query"
    return "no_relevant_docs"


def no_relevant_docs(state: GraphState) -> dict:
    return {"answer": "I couldn't find anything in the Orbitra knowledge base that answers this. "
                      "Try rephrasing, or raise an OrbitDesk ticket with the relevant team."}


def generate(state: GraphState) -> dict:
    chain = prompt | llm
    response = chain.invoke({
        "context": format_docs(state["documents"]),
        "question": state["question"],
    })
    return {"answer": response.content, "generation_attempts": 1}


def revise_answer(state: GraphState) -> dict:
    claims = "\n".join(f"- {c}" for c in state["unsupported_claims"])
    response = (revise_prompt | llm).invoke({
        "context": format_docs(state["documents"]),
        "question": state["question"],
        "answer": state["answer"],
        "claims": claims,
    })
    return {"answer": response.content, "generation_attempts": state["generation_attempts"] + 1}


def check_support(state: GraphState) -> dict:
    grade = support_checker.invoke({
        "context": format_docs(state["documents"]),
        "question": state["question"],  # the user's own numbers are valid inputs to the answer
        "answer": state["answer"],
    })
    return {"support": grade.support, "unsupported_claims": grade.unsupported_claims}


# END is just the string "__end__", so a router can finish the graph directly
def route_after_support(state: GraphState) -> Literal["check_useful", "revise_answer", "flag_unsupported"]:
    if state["support"] == "fully":
        return "check_useful"
    if state["generation_attempts"] < MAX_GENERATIONS:
        return "revise_answer"
    return "flag_unsupported"


def flag_unsupported(state: GraphState) -> dict:
    claims = "\n".join(f"- {c}" for c in state["unsupported_claims"])
    return {"answer": state["answer"] + "\n\n⚠️ I couldn't verify these parts against the "
                                        "knowledge base:\n" + claims}


def check_useful(state: GraphState) -> dict:
    grade = usefulness_checker.invoke({"question": state["question"], "answer": state["answer"]})
    return {"is_useful": grade.is_useful, "usefulness_reason": grade.reason}


# a grounded "I don't know" is still a fine final answer once the rewrite is used up
def route_after_useful(state: GraphState) -> Literal["rewrite_query", "__end__"]:
    if state["is_useful"] or state.get("rewrite_count", 0) >= MAX_REWRITES:
        return END
    return "rewrite_query"


def rewrite_query(state: GraphState) -> dict:
    new_query = rewriter.invoke({
        "question": state["question"],
        "previous_query": state.get("search_query") or state["question"],
    }).content.strip()
    return {"search_query": new_query, "rewrite_count": state.get("rewrite_count", 0) + 1}


def generate_direct(state: GraphState) -> dict:
    response = (direct_prompt | llm).invoke({"question": state["question"]})
    return {"answer": response.content}


builder = StateGraph(GraphState)
builder.add_node("decide_retrieval", decide_retrieval)
builder.add_node("retrieve", retrieve)
builder.add_node("grade_documents", grade_documents)
builder.add_node("generate", generate)
builder.add_node("check_support", check_support)
builder.add_node("revise_answer", revise_answer)
builder.add_node("flag_unsupported", flag_unsupported)
builder.add_node("check_useful", check_useful)
builder.add_node("rewrite_query", rewrite_query)
builder.add_node("no_relevant_docs", no_relevant_docs)
builder.add_node("generate_direct", generate_direct)
builder.add_edge(START, "decide_retrieval")
builder.add_conditional_edges("decide_retrieval", route_after_decision)
builder.add_edge("retrieve", "grade_documents")
builder.add_conditional_edges("grade_documents", route_after_grading)
builder.add_edge("generate", "check_support")
builder.add_conditional_edges("check_support", route_after_support)
builder.add_edge("revise_answer", "check_support")
builder.add_conditional_edges("check_useful", route_after_useful)
builder.add_edge("rewrite_query", "retrieve")  # loop back with the new search query
builder.add_edge("flag_unsupported", END)
builder.add_edge("no_relevant_docs", END)
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
            elif node == "grade_documents":
                for g in update["doc_grades"]:
                    print(f"  {'✓' if g['relevant'] else '✗'} [{g['doc_id']}] {g['reason']}")
            elif node == "check_support":
                print(f"  support={update['support']}")
                for c in update["unsupported_claims"]:
                    print(f"  ✗ {c}")
            elif node == "check_useful":
                print(f"  useful={update['is_useful']}  ({update['usefulness_reason']})")
            elif node == "rewrite_query":
                print(f"  🔁 new query: {update['search_query']!r}")
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
