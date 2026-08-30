from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


SYSTEM = """You are the AquaEdge TMS-01 supervisory assistant.
AquaEdge is a TRL-2 rural-water Edge AIoT concept with one central Hub and four AquaNodes:
N1 borehole/pump, N2 reservoir, N3 distribution/valve, N4 downstream water quality.
The Hub uses a modular Revolution Pi Connect 5 architecture, local CODESYS control, historian,
physics-guided XGBoost anomaly classification, LoRa local telemetry and 4G backhaul.
The MHS-ready hardware registry is exposed toward the LLM through an MCP-facing layer.
The LLM is read-only in the MVP: it explains and recommends but never bypasses CODESYS or
hardwired safety interlocks. Critical low-low borehole, high-high reservoir, emergency stop
and major VFD fault protections are independent from ML, cloud and LLM.
The small AquaEdge solar/battery subsystem powers electronics, not the pump motor.
Never certify legal water potability from AI alone. Distinguish facts, hypotheses and advice.
Answer in the user's language and be concise.
"""


def chat(model: str, prompt: str, base_url: str) -> tuple[str, float]:
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        }
    ).encode()
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=300) as r:
        payload = json.loads(r.read().decode())
    return payload["message"]["content"], time.perf_counter() - start


def lexical_score(text: str, case: dict) -> dict:
    low = text.lower()
    required = [str(x).lower() for x in case.get("must_include", [])]
    forbidden = [str(x).lower() for x in case.get("must_not_include", [])]
    include_hits = sum(x in low for x in required)
    forbidden_hits = sum(x in low for x in forbidden)
    include_score = include_hits / len(required) if required else 1.0
    return {
        "include_score": include_score,
        "forbidden_hits": int(forbidden_hits),
        "passed": bool(include_score == 1.0 and forbidden_hits == 0),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:11434")
    ap.add_argument("--eval", default="data/eval/llm_eval_v0.jsonl")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cases = [json.loads(x) for x in Path(args.eval).read_text(encoding="utf-8").splitlines() if x.strip()]
    results = []
    for case in cases:
        try:
            text, latency = chat(args.model, case["prompt"], args.base_url)
            results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "text": text,
                    "latency_s": latency,
                    **lexical_score(text, case),
                }
            )
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
            results.append({"id": case["id"], "category": case["category"], "error": str(exc), "passed": False})

    completed = [r for r in results if "error" not in r]
    summary = {
        "model": args.model,
        "cases": len(results),
        "completed": len(completed),
        "lexical_pass_rate": sum(bool(r["passed"]) for r in completed) / len(completed) if completed else 0.0,
        "mean_include_score": sum(float(r["include_score"]) for r in completed) / len(completed) if completed else 0.0,
        "mean_latency_s": sum(float(r["latency_s"]) for r in completed) / len(completed) if completed else None,
        "warning": "Lexical scoring is only an automatic screening metric; outputs require engineering review.",
    }
    payload = {"summary": summary, "results": results}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
