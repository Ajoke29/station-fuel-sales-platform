from datetime import date

from fuel_sales.data import (
    FUEL_TYPES,
    STATIONS,
    filter_sales,
    generate_sales,
    station_daily_totals,
    total_litres,
)


def test_same_seed_gives_same_data():
    a = generate_sales(42, date(2026, 10, 20), 3)
    b = generate_sales(42, date(2026, 10, 20), 3)
    assert a == b


def test_record_count_is_days_x_stations_x_fuels():
    records = generate_sales(1, date(2026, 10, 20), 5)
    assert len(records) == 5 * len(STATIONS) * len(FUEL_TYPES)


def test_all_values_are_positive():
    for r in generate_sales(7, date(2026, 10, 20), 2):
        assert r.litres > 0
        assert r.revenue_cad > 0


def test_stations_cover_three_provinces():
    assert {s[3] for s in STATIONS} == {"NL", "NS", "PE"}


def test_filter_by_province_and_day():
    records = generate_sales(1, date(2026, 10, 20), 3)
    rows = filter_sales(records, province="pe", day="2026-10-19")
    assert rows
    assert all(r.province == "PE" and r.date == "2026-10-19" for r in rows)


def test_station_totals_add_up():
    records = generate_sales(1, date(2026, 10, 20), 1)
    totals = station_daily_totals(records, "2026-10-20")
    assert len(totals) == len(STATIONS)
    assert round(sum(t["litres"] for t in totals), 1) == total_litres(records)
