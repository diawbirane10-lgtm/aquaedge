import json
from pathlib import Path

from app.ml.loop import train_cascade
from app.telemetry.synthetic import generate


if __name__ == "__main__":
    df = generate()
    result = train_cascade(df)
    payload = {
        "accuracy": result.accuracy,
        "macro_f1": result.macro_f1,
        "per_class": {
            k: {
                "precision": v["precision"],
                "recall": v["recall"],
                "f1": v["f1-score"],
            }
            for k, v in result.report.items()
            if isinstance(v, dict) and "f1-score" in v and k not in {"macro avg", "weighted avg"}
        },
        "note": "Synthetic unseen-episode evaluation only; not field accuracy.",
    }
    out = Path("results/cycle3_runtime.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
