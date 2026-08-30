from app.rules.safety import SafetyState, authorize_request


def test_llm_cannot_write_actuator() -> None:
    ok, reason = authorize_request("llm", "pump.start", SafetyState())
    assert not ok
    assert "disabled" in reason.lower()


def test_low_low_blocks_pump_start() -> None:
    state = SafetyState(borehole_low_low=True)
    ok, _ = authorize_request("codesys", "pump.start", state)
    assert not ok


def test_normal_codesys_request_can_continue() -> None:
    ok, _ = authorize_request("codesys", "pump.start", SafetyState())
    assert ok
