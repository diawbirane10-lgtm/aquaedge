from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


NodeId = Literal["N1", "N2", "N3", "N4", "HUB"]


class TelemetrySnapshot(BaseModel):
    timestamp: datetime
    node_id: NodeId
    well_level_m: float | None = None
    flow_m3h: float | None = None
    pressure_bar: float | None = None
    pump_power_kw: float | None = None
    tank_level_pct: float | None = None
    valve_open_pct: float | None = None
    nitrate_mg_l: float | None = None
    turbidity_ntu: float | None = None
    conductivity_us_cm: float | None = None
    water_temp_c: float | None = None
    battery_v: float | None = None
    battery_soc_pct: float | None = None


class AnomalyAssessment(BaseModel):
    state: Literal[
        "normal",
        "leak",
        "pump_fault",
        "dry_run",
        "quality_drift",
        "sensor_fault",
        "unknown",
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = []
    recommendation: str


class LLMAdvice(BaseModel):
    summary: str
    evidence: list[str]
    recommended_checks: list[str]
    safety_note: str
    actuator_request_allowed: bool = False
