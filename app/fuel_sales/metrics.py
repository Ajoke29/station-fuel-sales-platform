"""Prometheus metrics exposed on /metrics."""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

REGISTRY = CollectorRegistry()

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests handled, by method, route and status code.",
    ["method", "path", "status"],
    registry=REGISTRY,
)

HTTP_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Time spent handling HTTP requests.",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
    registry=REGISTRY,
)

LITRES_SOLD = Gauge(
    "fuel_sales_litres_sold",
    "Total litres sold across all stations in the loaded sample period.",
    registry=REGISTRY,
)

LITRES_BY_PROVINCE = Gauge(
    "fuel_sales_litres_by_province",
    "Litres sold in the loaded sample period, by province and fuel type.",
    ["province", "fuel_type"],
    registry=REGISTRY,
)

STATIONS_REPORTING = Gauge(
    "fuel_sales_stations_reporting",
    "Number of stations with sales data for the latest day.",
    registry=REGISTRY,
)
