"""Run all eval questions through the Self-RAG graph and LLM-judge each answer. Resumable.

Usage (from the project root): uv run eval/run_eval.py eval/results_<name>.jsonl [QID ...]
Already-answered qids in the results file are skipped, so re-run the same command to resume.
Pass qids (e.g. Q004 Q011) to run only those questions.
"""
import json, sys, time
from pathlib import Path
from typing import Literal
sys.path.insert(0, ".")
import groq
from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import main

OUT = Path(sys.argv[1])
TPM = 8000

class Verdict(BaseModel):
    verdict: Literal["correct", "partial", "incorrect"] = Field(description=
        "'correct' if the answer contains the key facts of the reference and nothing that contradicts it; "
        "'partial' if some key facts are missing, or it only asks a clarifying question where the reference "
        "gives a full answer; 'incorrect' if it contradicts the reference, uses outdated values, or answers "
        "when the reference says the information is not available.")
    reason: str = Field(description="One or two sentences.")

judge = ChatPromptTemplate.from_messages([
    ("system",
     "You grade answers from OrbitBot, an internal company assistant, against a reference answer. "
     "If the reference says the information is not in the knowledge base or needs a personal-data tool, "
     "an answer that says it cannot find or access it is correct (redirecting the user is a bonus). "
     "If the reference says the agent should ask for details, asking with the right options is correct."),
    ("human", "Question: {question}\n\nReference answer: {ground_truth}\n\nOrbitBot's answer:\n{answer}"),
]) | main.llm.with_structured_output(Verdict)

done = {json.loads(l)["qid"] for l in OUT.open()} if OUT.exists() else set()
qs = [json.loads(l) for l in open("eval/eval_questions.jsonl")]
only = set(sys.argv[2:])
todo = [q for q in qs if q["qid"] not in done and (not only or q["qid"] in only)]
print(f"{len(done)} done, {len(todo)} to go", flush=True)

for n, q in enumerate(todo, 1):
    for attempt in range(2):
        t0 = time.perf_counter()
        rec = {"qid": q["qid"], "type": q["type"], "difficulty": q["difficulty"], "gold_docs": q["gold_docs"],
               "path": [], "retrieved": [], "kept": [], "search_query": None}
        try:
            with get_usage_metadata_callback() as cb:
                for step in main.app.stream({"question": q["question"]}, stream_mode="updates"):
                    for node, u in step.items():
                        rec["path"].append(node)
                        if node == "retrieve":
                            rec["retrieved"].append([(d.metadata.get("doc_id"), d.metadata.get("status")) for d in u["documents"]])
                        elif node == "grade_documents":
                            rec["kept"] = [(d.metadata.get("doc_id"), d.metadata.get("status")) for d in u["documents"]]
                        elif node == "rewrite_query":
                            rec["search_query"] = u["search_query"]
                        elif node == "check_support":
                            rec["support"] = u["support"]; rec["unsupported_claims"] = u["unsupported_claims"]
                        elif node == "check_useful":
                            rec["useful"] = u["is_useful"]
                        if "answer" in u:
                            rec["answer"] = u["answer"]
                rec["graph_seconds"] = round(time.perf_counter() - t0, 1)
                v = judge.invoke({"question": q["question"], "ground_truth": q["ground_truth"], "answer": rec["answer"]})
                rec["verdict"], rec["judge_reason"] = v.verdict, v.reason
            rec["tokens"] = sum(u["total_tokens"] for u in cb.usage_metadata.values())
            break
        except groq.RateLimitError as e:
            msg = str(e)
            if "per day" in msg or "(TPD)" in msg or "(RPD)" in msg:
                print(f"\nDAILY LIMIT reached at {q['qid']}: {msg[:300]}\nRe-run later to resume.", flush=True)
                sys.exit(2)
            print(f"  {q['qid']}: per-minute limit after retries, waiting 60s", flush=True)
            time.sleep(60)
    else:
        print(f"  {q['qid']}: failed twice, skipping", flush=True); continue

    with OUT.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    elapsed = time.perf_counter() - t0
    print(f"[{len(done)+n}/{len(qs)}] {q['qid']} {q['type']:<16} {rec['verdict']:<9} "
          f"{rec['tokens']:>5} tok {elapsed:5.1f}s  path={'>'.join(p[:6] for p in rec['path'])}", flush=True)
    time.sleep(max(0, rec["tokens"] / TPM * 60 - elapsed))   # stay under the per-minute token budget
print("ALL DONE", flush=True)
