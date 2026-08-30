from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


CLASSES = ["normal", "leak", "pump_fault", "dry_run", "quality_drift", "sensor_fault"]


def generate(seed: int = 42, episodes_per_class: int = 12, steps: int = 50) -> pd.DataFrame:
    """Generate TRL-2 synthetic telemetry episodes.

    The generator intentionally introduces episode-to-episode operating-point
    variation so a model cannot succeed simply by memorizing absolute values.
    """
    rng = np.random.default_rng(seed)
    rows: list[dict[str, float | int | str]] = []
    episode = 0

    for label in CLASSES:
        for e in range(episodes_per_class):
            episode += 1
            severity = rng.uniform(0.35, 1.0)
            base_flow = rng.normal(8.5, 0.8)
            base_pressure = rng.normal(2.8, 0.22)
            base_well = rng.normal(18.0, 1.3)
            base_power = rng.normal(3.0, 0.22)
            base_tank = rng.uniform(45, 82)
            base_no3 = rng.normal(39, 3.5)
            base_turb = rng.normal(1.2, 0.25)
            base_cond = rng.normal(780, 70)
            base_temp = rng.normal(24, 2.2)
            phase = rng.uniform(0, 2 * np.pi)

            for t in range(steps):
                demand = 1 + 0.10 * np.sin(2 * np.pi * t / steps + phase) + rng.normal(0, 0.025)
                flow = base_flow * demand + rng.normal(0, 0.32)
                pressure = base_pressure - 0.20 * (demand - 1) + rng.normal(0, 0.09)
                well = base_well + 0.01 * t + rng.normal(0, 0.12)
                power = base_power * demand + rng.normal(0, 0.10)
                tank = base_tank + 4 * np.sin(2 * np.pi * t / 70 + phase) - 0.03 * t + rng.normal(0, 0.7)
                nitrate = base_no3 + rng.normal(0, 1.1)
                turbidity = base_turb + rng.normal(0, 0.12)
                conductivity = base_cond + rng.normal(0, 22)
                temperature = base_temp + 1.2 * np.sin(2 * np.pi * t / steps) + rng.normal(0, 0.25)
                valve = 95 + rng.normal(0, 2)
                battery = 25.7 + rng.normal(0, 0.18)
                soc = 78 + 8 * np.sin(2 * np.pi * t / steps + 1) + rng.normal(0, 2)
                progress = max(0.0, (t - 8) / max(1, steps - 8))

                if label == "leak":
                    flow += severity * (0.7 + 2.2 * progress)
                    pressure -= severity * (0.18 + 0.75 * progress)
                    tank -= severity * (1.5 + 7.5 * progress)
                elif label == "pump_fault":
                    power += severity * (0.35 + 1.15 * progress)
                    flow -= severity * (0.25 + 1.0 * progress)
                    pressure -= severity * (0.05 + 0.28 * progress)
                elif label == "dry_run":
                    well += severity * (0.5 + 6.0 * progress)
                    flow -= severity * (0.25 + 2.1 * progress)
                    pressure -= severity * (0.08 + 0.55 * progress)
                    power += severity * (0.10 + 0.40 * progress)
                elif label == "quality_drift":
                    nitrate += severity * (1.0 + 19 * progress)
                    turbidity += severity * (0.05 + 2.8 * progress)
                    conductivity += severity * (10 + 150 * progress)
                elif label == "sensor_fault":
                    mode = e % 4
                    if mode == 0:
                        pressure += severity * (0.5 if t < 25 else -0.7) + rng.normal(0, 0.22)
                    elif mode == 1:
                        flow = base_flow + 0.02 * rng.normal()
                    elif mode == 2:
                        tank += rng.normal(0, 3.5 * severity)
                    else:
                        nitrate += rng.normal(0, 6 * severity)

                rows.append(
                    {
                        "episode_id": episode,
                        "t": t,
                        "label": label,
                        "well_level_m": well,
                        "flow_m3h": flow,
                        "pressure_bar": pressure,
                        "pump_power_kw": power,
                        "tank_level_pct": tank,
                        "valve_open_pct": valve,
                        "nitrate_mg_l": nitrate,
                        "turbidity_ntu": turbidity,
                        "conductivity_us_cm": conductivity,
                        "water_temp_c": temperature,
                        "battery_v": battery,
                        "battery_soc_pct": soc,
                    }
                )

    return pd.DataFrame(rows)


def write_csv(path: str | Path, **kwargs: object) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    generate(**kwargs).to_csv(out, index=False)
    return out
