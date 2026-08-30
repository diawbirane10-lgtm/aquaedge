from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score
from xgboost import XGBClassifier


CLASSES = ["normal", "leak", "pump_fault", "dry_run", "quality_drift", "sensor_fault"]
PROCESS_CLASSES = CLASSES[:5]


@dataclass(slots=True)
class LoopResult:
    accuracy: float
    macro_f1: float
    report: dict


def _episode_split(df: pd.DataFrame) -> tuple[list[int], list[int]]:
    train_eps: list[int] = []
    test_eps: list[int] = []
    for label in CLASSES:
        eps = sorted(df.loc[df.label == label, "episode_id"].unique())
        if len(eps) < 4:
            raise ValueError("Need at least 4 episodes per class")
        n_test = max(1, round(len(eps) * 0.25))
        train_eps += list(eps[:-n_test])
        test_eps += list(eps[-n_test:])
    return train_eps, test_eps


def engineer_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    d = df.copy()
    base_cols = [
        "well_level_m",
        "flow_m3h",
        "pressure_bar",
        "pump_power_kw",
        "tank_level_pct",
        "nitrate_mg_l",
        "turbidity_ntu",
        "conductivity_us_cm",
        "water_temp_c",
        "battery_v",
        "battery_soc_pct",
    ]
    features: list[str] = []

    for col in base_cols:
        ref_mean = d.groupby("episode_id")[col].transform(lambda s: float(s.iloc[:8].mean()))
        ref_std = d.groupby("episode_id")[col].transform(
            lambda s: max(float(s.iloc[:8].std(ddof=0)), 0.05)
        )
        z = f"z_{col}"
        d[z] = (d[col] - ref_mean) / ref_std
        features.append(z)
        g = d.groupby("episode_id")[z]
        for w in (5, 10):
            for stat in ("mean", "std"):
                name = f"{z}_{'ma' if stat == 'mean' else 'std'}{w}"
                if stat == "mean":
                    d[name] = g.transform(lambda s, ww=w: s.rolling(ww, min_periods=2).mean()).fillna(0)
                else:
                    d[name] = g.transform(lambda s, ww=w: s.rolling(ww, min_periods=2).std()).fillna(0)
                features.append(name)
            rname = f"{z}_range{w}"
            d[rname] = g.transform(
                lambda s, ww=w: s.rolling(ww, min_periods=2).max()
                - s.rolling(ww, min_periods=2).min()
            ).fillna(0)
            features.append(rname)
        delta = f"{z}_delta5"
        d[delta] = g.transform(lambda s: s - s.shift(5)).fillna(0)
        features.append(delta)

    d["efficiency_proxy"] = (
        d["flow_m3h"].clip(lower=0.5) * d["pressure_bar"].clip(lower=0.05)
    ) / d["pump_power_kw"].clip(lower=0.2)
    ref = d.groupby("episode_id")["efficiency_proxy"].transform(lambda s: float(s.iloc[:8].mean()))
    std = d.groupby("episode_id")["efficiency_proxy"].transform(
        lambda s: max(float(s.iloc[:8].std(ddof=0)), 0.03)
    )
    d["z_efficiency_proxy"] = (d["efficiency_proxy"] - ref) / std
    features.append("z_efficiency_proxy")

    d["leak_score"] = (
        d["z_flow_m3h"].clip(lower=0) * 0.9
        + (-d["z_pressure_bar"]).clip(lower=0) * 0.7
        + (-d["z_tank_level_pct"]).clip(lower=0) * 0.25
    )
    d["pump_score"] = (
        d["z_pump_power_kw"].clip(lower=0) * 0.8
        + (-d["z_efficiency_proxy"]).clip(lower=0) * 0.6
    )
    d["dry_score"] = (
        d["z_well_level_m"].clip(lower=0) * 0.7
        + (-d["z_flow_m3h"]).clip(lower=0) * 0.6
        + (-d["z_pressure_bar"]).clip(lower=0) * 0.25
    )
    d["quality_score"] = (
        d["z_nitrate_mg_l"].clip(lower=0) * 0.7
        + d["z_turbidity_ntu"].clip(lower=0) * 0.5
        + d["z_conductivity_us_cm"].clip(lower=0) * 0.35
    )
    features += ["leak_score", "pump_score", "dry_score", "quality_score"]

    sensor_features: list[str] = []
    for col in [
        "flow_m3h",
        "pressure_bar",
        "tank_level_pct",
        "nitrate_mg_l",
        "turbidity_ntu",
        "conductivity_us_cm",
    ]:
        for suffix in ("std5", "std10", "range5", "range10", "delta5"):
            sensor_features.append(f"z_{col}_{suffix}")
        sensor_features.append(f"z_{col}")

    return d.replace([np.inf, -np.inf], 0).fillna(0), features, sensor_features


def train_cascade(df: pd.DataFrame, sensor_threshold: float = 0.65) -> LoopResult:
    d, process_features, sensor_features = engineer_features(df)
    train_eps, test_eps = _episode_split(d)
    tr = d.episode_id.isin(train_eps) & (d.t >= 10)
    te = d.episode_id.isin(test_eps) & (d.t >= 10)

    sensor_y = (d.label == "sensor_fault").astype(int)
    sensor_model = XGBClassifier(
        n_estimators=350,
        max_depth=4,
        learning_rate=0.035,
        subsample=0.92,
        colsample_bytree=0.9,
        reg_lambda=2,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=31,
        n_jobs=4,
    )
    sensor_model.fit(d.loc[tr, sensor_features], sensor_y.loc[tr])

    process_train = tr & (d.label != "sensor_fault")
    process_map = {c: i for i, c in enumerate(PROCESS_CLASSES)}
    process_model = XGBClassifier(
        n_estimators=700,
        max_depth=5,
        learning_rate=0.025,
        min_child_weight=2,
        subsample=0.92,
        colsample_bytree=0.82,
        reg_lambda=2.5,
        reg_alpha=0.08,
        objective="multi:softprob",
        num_class=len(PROCESS_CLASSES),
        eval_metric="mlogloss",
        random_state=23,
        n_jobs=4,
    )
    process_model.fit(
        d.loc[process_train, process_features],
        d.loc[process_train, "label"].map(process_map),
    )

    sensor_p = sensor_model.predict_proba(d.loc[te, sensor_features])[:, 1]
    process_p = process_model.predict(d.loc[te, process_features])
    pred = np.array(
        [5 if sp >= sensor_threshold else int(pp) for sp, pp in zip(sensor_p, process_p)]
    )
    class_map = {c: i for i, c in enumerate(CLASSES)}
    truth = d.loc[te, "label"].map(class_map).to_numpy()
    report = classification_report(
        truth, pred, target_names=CLASSES, output_dict=True, zero_division=0
    )
    return LoopResult(
        accuracy=float(accuracy_score(truth, pred)),
        macro_f1=float(f1_score(truth, pred, average="macro")),
        report=report,
    )
