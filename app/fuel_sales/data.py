"""Fictional stations and seeded (repeatable) daily fuel sales.

Nothing here is real company data. Station names are made up and the
numbers come from a seeded random generator, so every run gives the
same results, which keeps tests and demos predictable.
"""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from datetime import date, timedelta

FUEL_TYPES = ("regular", "premium", "diesel")

# (station_id, name, town, province)
STATIONS: tuple[tuple[str, str, str, str], ...] = (
    ("NL-001", "Signal Hill Fuel Stop", "St. John's", "NL"),
    ("NL-002", "Quidi Vidi Gas & Go", "St. John's", "NL"),
    ("NL-003", "Conception Bay Corner", "Conception Bay South", "NL"),
    ("NL-004", "Gander Lake Fuel Bar", "Gander", "NL"),
    ("NL-005", "Humber Valley Pumps", "Corner Brook", "NL"),
    ("NL-006", "Exploits River Station", "Grand Falls-Windsor", "NL"),
    ("NS-001", "Harbourfront Fuel Hub", "Halifax", "NS"),
    ("NS-002", "Cobequid Pass Stop", "Truro", "NS"),
    ("NS-003", "Cape Breton Crossroads", "Sydney", "NS"),
    ("NS-004", "Annapolis Valley Pumps", "Kentville", "NS"),
    ("PE-001", "Red Sands Fuel & Snack", "Charlottetown", "PE"),
    ("PE-002", "Confederation Trail Gas", "Summerside", "PE"),
)


@dataclass(frozen=True)
class SaleRecord:
    date: str
    station_id: str
    station_name: str
    town: str
    province: str
    fuel_type: str
    litres: float
    revenue_cad: float

    def to_dict(self) -> dict:
        return asdict(self)


# Rough fictional price per litre (CAD) and daily volume range per fuel type.
_PRICE = {"regular": 1.62, "premium": 1.89, "diesel": 1.78}
_VOLUME = {"regular": (2500, 6500), "premium": (300, 1100), "diesel": (900, 3200)}


def generate_sales(seed: int, end_date: date, days: int) -> list[SaleRecord]:
    """Return `days` days of sales (ending on `end_date`) for every station."""
    rng = random.Random(seed)
    records: list[SaleRecord] = []
    for offset in range(days - 1, -1, -1):
        day = end_date - timedelta(days=offset)
        weekend_boost = 1.15 if day.weekday() >= 4 else 1.0
        for station_id, name, town, province in STATIONS:
            for fuel in FUEL_TYPES:
                low, high = _VOLUME[fuel]
                litres = round(rng.uniform(low, high) * weekend_boost, 1)
                price = _PRICE[fuel] + rng.uniform(-0.04, 0.04)
                records.append(
                    SaleRecord(
                        date=day.isoformat(),
                        station_id=station_id,
                        station_name=name,
                        town=town,
                        province=province,
                        fuel_type=fuel,
                        litres=litres,
                        revenue_cad=round(litres * price, 2),
                    )
                )
    return records


def filter_sales(
    records: list[SaleRecord],
    *,
    province: str | None = None,
    station_id: str | None = None,
    day: str | None = None,
) -> list[SaleRecord]:
    result = records
    if province:
        result = [r for r in result if r.province == province.upper()]
    if station_id:
        result = [r for r in result if r.station_id == station_id.upper()]
    if day:
        result = [r for r in result if r.date == day]
    return result


def station_daily_totals(records: list[SaleRecord], day: str) -> list[dict]:
    """One row per station for a given day, all fuel types added together."""
    totals: dict[str, dict] = {}
    for r in records:
        if r.date != day:
            continue
        row = totals.setdefault(
            r.station_id,
            {
                "station_id": r.station_id,
                "station_name": r.station_name,
                "town": r.town,
                "province": r.province,
                "litres": 0.0,
                "revenue_cad": 0.0,
            },
        )
        row["litres"] = round(row["litres"] + r.litres, 1)
        row["revenue_cad"] = round(row["revenue_cad"] + r.revenue_cad, 2)
    return sorted(totals.values(), key=lambda x: x["station_id"])


def total_litres(records: list[SaleRecord]) -> float:
    return round(sum(r.litres for r in records), 1)
