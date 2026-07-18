from fastapi.testclient import TestClient

from deriv_advisor.web import create_app


def test_demo_mode_suggestions():
    app = create_app(demo_mode=True)
    client = TestClient(app)
    health = client.get("/api/health").json()
    assert health["mode"] == "demo"
    response = client.post("/api/suggestions", json={"instagram_text": ""})
    assert response.status_code == 200
    payload = response.json()
    assert payload["account"]["loginid"] == "VRTC-DEMO"
    assert payload["suggestions"]
    assert payload["suggestions"][0]["symbol"] in {"R_75", "R_100", "R_50"}
