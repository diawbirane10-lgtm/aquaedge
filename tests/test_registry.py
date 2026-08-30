from app.mhs_registry.registry import default_registry


def test_default_registry_has_four_nodes() -> None:
    r = default_registry()
    ids = {d["device_id"] for d in r.discover()}
    assert ids == {"N1", "N2", "N3", "N4"}


def test_llm_registry_request_is_read_only() -> None:
    r = default_registry()
    denied = r.request_capability("N3", "valve_close.request")
    assert denied["status"] == "denied"


def test_registry_can_return_measurement() -> None:
    r = default_registry()
    r.update_state("N4.nitrate.read", 47.2)
    response = r.request_capability("N4", "nitrate.read")
    assert response["status"] == "ok"
    assert response["value"] == 47.2
