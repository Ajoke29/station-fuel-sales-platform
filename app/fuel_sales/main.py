"""FastAPI application: HTML dashboard, JSON API, health checks and metrics."""

from __future__ import annotations

import html
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from . import __version__
from .config import Settings
from .data import (
    FUEL_TYPES,
    STATIONS,
    filter_sales,
    generate_sales,
    station_daily_totals,
    total_litres,
)
from .metrics import (
    HTTP_LATENCY,
    HTTP_REQUESTS,
    LITRES_BY_PROVINCE,
    LITRES_SOLD,
    REGISTRY,
    STATIONS_REPORTING,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("fuel_sales")


class AppState:
    def __init__(self) -> None:
        self.ready = False
        self.settings = Settings()
        self.records: list = []


state = AppState()


def load_data(settings: Settings) -> None:
    """Load the seeded sample data and refresh the business gauges."""
    state.settings = settings
    state.records = generate_sales(settings.seed, settings.end_date, settings.sample_days)
    LITRES_SOLD.set(total_litres(state.records))
    for province in sorted({s[3] for s in STATIONS}):
        for fuel in FUEL_TYPES:
            subset = [r for r in state.records if r.province == province and r.fuel_type == fuel]
            LITRES_BY_PROVINCE.labels(province=province, fuel_type=fuel).set(total_litres(subset))
    latest = settings.end_date.isoformat()
    STATIONS_REPORTING.set(len({r.station_id for r in state.records if r.date == latest}))
    state.ready = True
    log.info(
        "loaded %d sales records (env=%s, days=%d)",
        len(state.records),
        settings.app_env,
        settings.sample_days,
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_data(Settings.from_env())
    yield
    state.ready = False


app = FastAPI(
    title="Station Fuel Sales",
    version=__version__,
    description="Fictional daily fuel sales for a multi-site fuel retailer (demo data).",
    lifespan=lifespan,
)


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path = getattr(route, "path", "unmatched")
        HTTP_REQUESTS.labels(request.method, path, str(status)).inc()
        HTTP_LATENCY.labels(request.method, path).observe(time.perf_counter() - start)


@app.get("/healthz", tags=["health"])
def healthz() -> dict:
    """Liveness: the process is up and able to answer."""
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> JSONResponse:
    """Readiness: data is loaded and the app can serve traffic."""
    if not state.ready:
        return JSONResponse({"status": "not ready"}, status_code=503)
    return JSONResponse({"status": "ready", "records": len(state.records)})


@app.get("/metrics", tags=["health"])
def metrics() -> Response:
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/stations", tags=["api"])
def list_stations() -> list[dict]:
    return [
        {"station_id": sid, "station_name": name, "town": town, "province": prov}
        for sid, name, town, prov in STATIONS
    ]


@app.get("/api/sales", tags=["api"])
def list_sales(
    province: Optional[str] = Query(None, description="NL, NS or PE"),
    station_id: Optional[str] = Query(None, description="e.g. NL-001"),
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
) -> dict:
    if province and province.upper() not in {"NL", "NS", "PE"}:
        raise HTTPException(status_code=400, detail="province must be NL, NS or PE")
    rows = filter_sales(state.records, province=province, station_id=station_id, day=date)
    return {
        "count": len(rows),
        "total_litres": total_litres(rows),
        "total_revenue_cad": round(sum(r.revenue_cad for r in rows), 2),
        "sales": [r.to_dict() for r in rows],
    }


@app.get("/api/chaos/error", tags=["demo"], include_in_schema=False)
def chaos_error() -> None:
    """Return a 500 on purpose, only when CHAOS_ENABLED=true (used to demo alerts)."""
    if os.getenv("CHAOS_ENABLED", "false").lower() != "true":
        raise HTTPException(status_code=404, detail="Not Found")
    raise HTTPException(status_code=500, detail="simulated failure")


@app.get("/", response_class=HTMLResponse, tags=["ui"])
def dashboard() -> str:
    day = state.settings.end_date.isoformat()
    rows = station_daily_totals(state.records, day)
    body = "\n".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
        "<td class='num'>{:,.1f}</td><td class='num'>${:,.2f}</td></tr>".format(
            html.escape(r["station_id"]),
            html.escape(r["station_name"]),
            html.escape(r["town"]),
            html.escape(r["province"]),
            r["litres"],
            r["revenue_cad"],
        )
        for r in rows
    )
    grand_litres = sum(r["litres"] for r in rows)
    grand_revenue = sum(r["revenue_cad"] for r in rows)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Station Fuel Sales</title>
<style>
 body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1b2a3a; }}
 h1 {{ margin-bottom: .2rem; }}
 .sub {{ color: #5b6b7b; margin-top: 0; }}
 table {{ border-collapse: collapse; width: 100%; max-width: 960px; }}
 th, td {{ padding: .45rem .7rem; border-bottom: 1px solid #dde3ea; text-align: left; }}
 th {{ background: #0b3d61; color: #fff; }}
 td.num, th.num {{ text-align: right; }}
 tfoot td {{ font-weight: bold; }}
 .note {{ color: #7a8794; font-size: .85rem; margin-top: 1rem; }}
</style>
</head>
<body>
<h1>Station Fuel Sales</h1>
<p class="sub">Daily totals for {html.escape(day)} &middot; environment: {html.escape(state.settings.app_env)}</p>
<table>
<thead><tr><th>Station</th><th>Name</th><th>Town</th><th>Prov.</th>
<th class="num">Litres</th><th class="num">Revenue (CAD)</th></tr></thead>
<tbody>
{body}
</tbody>
<tfoot><tr><td colspan="4">All stations</td>
<td class="num">{grand_litres:,.1f}</td><td class="num">${grand_revenue:,.2f}</td></tr></tfoot>
</table>
<p class="note">Fictional demo data. JSON API: <a href="/api/sales">/api/sales</a> &middot;
<a href="/docs">API docs</a> &middot; <a href="/metrics">metrics</a></p>
</body>
</html>"""
