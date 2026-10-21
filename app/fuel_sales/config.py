"""Settings read from environment variables (supplied by a Kubernetes ConfigMap)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    app_env: str = "local"
    seed: int = 2026
    sample_days: int = 7
    end_date: date = field(default_factory=lambda: date(2026, 10, 20))

    @classmethod
    def from_env(cls) -> "Settings":
        end_raw = os.getenv("SALES_END_DATE", "2026-10-20")
        return cls(
            app_env=os.getenv("APP_ENV", "local"),
            seed=_get_int("SALES_SEED", 2026),
            sample_days=max(1, min(_get_int("SALES_SAMPLE_DAYS", 7), 90)),
            end_date=date.fromisoformat(end_raw),
        )
