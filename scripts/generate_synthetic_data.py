from pathlib import Path

from app.telemetry.synthetic import write_csv


if __name__ == "__main__":
    path = write_csv(Path("data/synthetic_telemetry/telemetry_v0.csv"))
    print(f"Wrote {path}")
