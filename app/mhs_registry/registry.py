from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Capability:
    name: str
    mode: str = "read"
    unit: str | None = None
    description: str = ""
    safety_critical: bool = False


@dataclass(slots=True)
class Device:
    device_id: str
    node_id: str
    device_type: str
    location: str
    capabilities: dict[str, Capability]
    upstream_of: list[str] = field(default_factory=list)
    downstream_of: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class HardwareRegistry:
    """MHS-ready registry used by the hub.

    This is intentionally a project abstraction, not a claim of formal MHS
    compliance. The public MHS specification may evolve; this registry keeps
    AquaEdge device identity, state and capabilities normalized in one place.
    """

    def __init__(self) -> None:
        self._devices: dict[str, Device] = {}
        self._state: dict[str, Any] = {}

    def register(self, device: Device) -> None:
        if device.device_id in self._devices:
            raise ValueError(f"Duplicate device_id: {device.device_id}")
        self._devices[device.device_id] = device

    def update_state(self, key: str, value: Any) -> None:
        self._state[key] = value

    def read_state(self, key: str) -> Any:
        return self._state.get(key)

    def get_device(self, device_id: str) -> Device:
        return self._devices[device_id]

    def discover(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for d in self._devices.values():
            out.append(
                {
                    "device_id": d.device_id,
                    "node_id": d.node_id,
                    "device_type": d.device_type,
                    "location": d.location,
                    "capabilities": {
                        k: {
                            "mode": c.mode,
                            "unit": c.unit,
                            "description": c.description,
                            "safety_critical": c.safety_critical,
                        }
                        for k, c in d.capabilities.items()
                    },
                    "upstream_of": d.upstream_of,
                    "downstream_of": d.downstream_of,
                }
            )
        return out

    def request_capability(self, device_id: str, capability: str) -> dict[str, Any]:
        device = self.get_device(device_id)
        cap = device.capabilities[capability]
        if cap.mode != "read":
            return {
                "status": "denied",
                "reason": "MVP LLM access is read-only; write requests require policy/human approval.",
            }
        key = f"{device_id}.{capability}"
        return {"status": "ok", "value": self.read_state(key), "unit": cap.unit}


def default_registry() -> HardwareRegistry:
    r = HardwareRegistry()
    r.register(
        Device(
            device_id="N1",
            node_id="N1",
            device_type="borehole_pump_node",
            location="Tamsoult / borehole sector",
            upstream_of=["N2"],
            capabilities={
                "groundwater_level.read": Capability("groundwater_level.read", unit="m"),
                "pressure.read": Capability("pressure.read", unit="bar"),
                "flow.read": Capability("flow.read", unit="m3/h"),
                "pump_status.read": Capability("pump_status.read"),
                "pump_fault.read": Capability("pump_fault.read"),
                "pump_start.request": Capability(
                    "pump_start.request", mode="request", safety_critical=True
                ),
                "pump_stop.request": Capability(
                    "pump_stop.request", mode="request", safety_critical=True
                ),
            },
        )
    )
    r.register(
        Device(
            device_id="N2",
            node_id="N2",
            device_type="reservoir_node",
            location="Tamsoult / reservoir sector",
            downstream_of=["N1"],
            upstream_of=["N3"],
            capabilities={
                "level.read": Capability("level.read", unit="%"),
                "high_high.read": Capability("high_high.read"),
            },
        )
    )
    r.register(
        Device(
            device_id="N3",
            node_id="N3",
            device_type="distribution_valve_node",
            location="Tamsoult / distribution sector",
            downstream_of=["N2"],
            upstream_of=["N4"],
            capabilities={
                "pressure.read": Capability("pressure.read", unit="bar"),
                "flow.read": Capability("flow.read", unit="m3/h"),
                "valve_position.read": Capability("valve_position.read", unit="%"),
                "valve_open.request": Capability(
                    "valve_open.request", mode="request", safety_critical=True
                ),
                "valve_close.request": Capability(
                    "valve_close.request", mode="request", safety_critical=True
                ),
            },
        )
    )
    r.register(
        Device(
            device_id="N4",
            node_id="N4",
            device_type="water_quality_node",
            location="Tamsoult / downstream sampling point",
            downstream_of=["N3"],
            capabilities={
                "nitrate.read": Capability("nitrate.read", unit="mg/L"),
                "turbidity.read": Capability("turbidity.read", unit="NTU"),
                "conductivity.read": Capability("conductivity.read", unit="uS/cm"),
                "temperature.read": Capability("temperature.read", unit="degC"),
            },
        )
    )
    return r
