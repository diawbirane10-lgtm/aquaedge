from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SafetyState:
    borehole_low_low: bool = False
    reservoir_high_high: bool = False
    emergency_stop: bool = False
    major_vfd_fault: bool = False

    @property
    def pump_permissive(self) -> bool:
        return not any(
            [
                self.borehole_low_low,
                self.reservoir_high_high,
                self.emergency_stop,
                self.major_vfd_fault,
            ]
        )


def authorize_request(source: str, action: str, state: SafetyState) -> tuple[bool, str]:
    """Return whether an action request may proceed to the normal control policy.

    This function does not replace the real hardwired chain. It encodes the MVP
    software policy so tests can ensure that LLM-originated requests never bypass
    safety assumptions.
    """
    if source.lower() == "llm":
        return False, "LLM direct actuator writes are disabled in the MVP."

    if action == "pump.start" and not state.pump_permissive:
        return False, "Pump start denied by safety permissive."

    if state.emergency_stop:
        return False, "Emergency stop is active."

    return True, "Request may proceed to CODESYS policy checks."
