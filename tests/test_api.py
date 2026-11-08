"""Pruebas unitarias con doble de pruebas, claramente NO modelo crediticio real."""

import numpy as np
from fastapi.testclient import TestClient

import app.main as main
from app.features import FEATURES
from app.service import ModelBundle


class FakeModel:
    classes_ = np.array([0, 1])

    def predict_proba(self, frame):
        assert list(frame.columns) == FEATURES
        p = 0.85 if frame.loc[0, "PAY_0"] >= 2 else 0.05
        return np.array([[1 - p, p]])


def request_example():
    return {
        "LIMIT_BAL": 120000,
        **{name: 0 for name in ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]},
        **{f"BILL_AMT{i}": 1000 for i in range(1, 7)},
        **{f"PAY_AMT{i}": 100 for i in range(1, 7)},
    }


def test_home():
    response = TestClient(main.app).get("/")
    assert response.status_code == 200
    assert "Riesgo crediticio" in response.text or "riesgo crediticio" in response.text


def test_model_missing_returns_503(monkeypatch):
    def unavailable():
        from app.service import ModelUnavailable
        raise ModelUnavailable("Sin modelo")

    monkeypatch.setattr(main, "load_bundle", unavailable)
    assert TestClient(main.app).get("/api/health").status_code == 503
    assert TestClient(main.app).post("/api/predecir", json=request_example()).status_code == 503


def test_model_response_and_threshold(monkeypatch):
    monkeypatch.setattr(main, "load_bundle", lambda: ModelBundle(
        estimator=FakeModel(),
        metadata={"modelo": "FAKE: unit testing only", "umbral": .14, "features": FEATURES},
    ))
    client = TestClient(main.app)
    assert client.get("/api/health").json()["estado"] == "listo"
    data = request_example()
    resp1 = client.post("/api/predecir", json=data)
    assert resp1.status_code == 200
    assert resp1.json()["puntaje_incumplimiento"] == .05
    assert resp1.json()["alerta"] is False
    data["PAY_0"] = 2
    resp2 = client.post("/api/predecir", json=data)
    assert resp2.status_code == 200
    assert resp2.json()["puntaje_incumplimiento"] == .85
    assert resp2.json()["alerta"] is True


def test_invalid_payload_and_extra_fields():
    client = TestClient(main.app)
    valid = request_example()
    for patch in [{"LIMIT_BAL": -10}, {"PAY_0": 11}, {"PAY_AMT1": -1}, {"BILL_AMT1": None}, {"AGE": 31}]:
        candidate = {**valid, **patch}
        response = client.post("/api/predecir", json=candidate)
        assert response.status_code == 422, (patch, response.text)
    valid.pop("PAY_AMT1")
    assert client.post("/api/predecir", json=valid).status_code == 422


def test_reject_string_and_nonfinite_inputs():
    client = TestClient(main.app)
    good = request_example()
    for sample in [{"LIMIT_BAL": "nan"}, {"PAY_0": 1.5}, {"BILL_AMT1": "infinity"}]:
        response=client.post("/api/predecir", json={**good,**sample})
        assert response.status_code == 422, sample
