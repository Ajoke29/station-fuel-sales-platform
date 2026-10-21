def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readyz(client):
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_readyz_not_ready(client):
    from fuel_sales.main import state

    state.ready = False
    try:
        assert client.get("/readyz").status_code == 503
    finally:
        state.ready = True


def test_dashboard_shows_stations(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Signal Hill Fuel Stop" in resp.text
    assert "Red Sands Fuel &amp; Snack" in resp.text


def test_sales_api_returns_records(client):
    data = client.get("/api/sales").json()
    assert data["count"] == len(data["sales"]) > 0
    assert data["total_litres"] > 0
    first = data["sales"][0]
    assert {"station_id", "province", "fuel_type", "litres", "revenue_cad"} <= first.keys()


def test_sales_api_filters(client):
    data = client.get("/api/sales", params={"province": "NS", "date": "2026-10-20"}).json()
    assert data["count"] == 4 * 3  # 4 NS stations x 3 fuel types
    assert all(s["province"] == "NS" for s in data["sales"])


def test_sales_api_rejects_bad_province(client):
    assert client.get("/api/sales", params={"province": "ON"}).status_code == 400


def test_stations_api(client):
    assert len(client.get("/api/stations").json()) == 12


def test_metrics_exposes_counters_and_gauge(client):
    client.get("/api/sales")
    body = client.get("/metrics").text
    assert 'http_requests_total{method="GET",path="/api/sales",status="200"}' in body
    assert "fuel_sales_litres_sold " in body
    assert "http_request_duration_seconds_bucket" in body


def test_unknown_route_is_counted_without_high_cardinality(client):
    client.get("/does-not-exist-123")
    body = client.get("/metrics").text
    assert 'path="unmatched",status="404"' in body
    assert "does-not-exist-123" not in body


def test_chaos_endpoint_disabled_by_default(client):
    assert client.get("/api/chaos/error").status_code == 404


def test_chaos_endpoint_returns_500_when_enabled(client, monkeypatch):
    monkeypatch.setenv("CHAOS_ENABLED", "true")
    assert client.get("/api/chaos/error").status_code == 500
