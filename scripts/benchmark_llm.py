from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from app.agents.aquaedge_agent import AquaEdgeAgent
from app.llm.providers import get_provider
from app.mhs_registry.registry import default_registry
from app.rag.simple_tfidf import Document, TfidfRetriever


def load_eval(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def default_docs() -> list[Document]:
    return [
        Document("hub", "The hub uses RevPi Connect 5 plus AIO DIO RO, CODESYS, local historian, machine learning and 4G backhaul."),
        Document("nodes", "N1 is borehole/pump; N2 reservoir; N3 distribution/valve; N4 downstream water quality."),
        Document("mhs", "The MHS-ready hardware registry normalizes device capabilities and state. MCP exposes tools/context to the LLM. It is not formal MHS certification."),
        Document("safety", "LLM writes are disabled in the MVP. Low-low borehole, high-high reservoir, emergency stop and major VFD fault are independent safety interlocks."),
        Document("power", "AquaEdge electronics use a dedicated PV battery 24 VDC supply. Pump motor power is separate."),
        Document("offline", "The hub is offline-first: local acquisition, CODESYS, historian, ML and alarms continue if WAN/4G is unavailable."),
    ]


def score_case(text: str, case: dict) -> dict:
    t = text.lower()
    required = [x.lower() for x in case.get("must_include", [])]
    forbidden = [x.lower() for x in case.get("must_not_include", [])]
    include_hits = sum(1 for x in required if x in t)
    forbidden_hits = sum(1 for x in forbidden if x in t)
    include_score = include_hits / len(required) if required else 1.0
    passed = include_score == 1.0 and forbidden_hits == 0
    return {
        "include_score": include_score,
        "forbidden_hits": forbidden_hits,
        "passed": passed,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--provider", default="ollama")
    p.add_argument("--model", default="gemma3:4b")
    p.add_argument("--eval", default="data/eval/llm_eval_v0.jsonl")
    p.add_argument("--output", default=None)
    args = p.parse_args()

    provider = get_provider(args.provider)
    agent = AquaEdgeAgent(
        provider=provider,
        model=args.model,
        registry=default_registry(),
        retriever=TfidfRetriever(default_docs()),
    )
    cases = load_eval(Path(args.eval))
    rows: list[dict] = []

    for case in cases:
        start = time.perf_counter()
        try:
            response = agent.answer(case["prompt"])
            latency = time.perf_counter() - start
            score = score_case(response.text, case)
            rows.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "latency_s": latency,
                    "text": response.text,
                    **score,
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "error": f"{type(exc).__name__}: {exc}",
                    "passed": False,
                }
            )

    success = [r for r in rows if "error" not in r]
    summary = {
        "provider": args.provider,
        "model": args.model,
        "cases": len(rows),
        "completed": len(success),
        "pass_rate": sum(bool(r.get("passed")) for r in success) / len(success) if success else 0.0,
        "mean_latency_s": sum(float(r["latency_s"]) for r in success) / len(success) if success else None,
        "note": "Automatic lexical score is a screening metric only; engineering review remains required.",
    }
    payload = {"summary": summary, "results": rows}
    out = Path(args.output or f"results/llm_{args.provider}_{args.model.replace(':', '_').replace('/', '_')}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
