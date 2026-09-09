#!/usr/bin/env python3
"""Light fixtures for estimate_revenue.py. Run: python3 scripts/test_estimate_revenue.py"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "estimate_revenue.py"


def run(args: list[str]) -> str:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def main() -> None:
    auto = run(
        [
            "--name", "Portland Auto Repair LLC",
            "--location", "Portland, PA",
            "--industry", "auto_services",
            "--location-tier", "rural",
            "--google-reviews", "151",
            "--google-rating", "4.8",
            "--google-velocity", "6",
            "--yelp-reviews", "5",
            "--years-open", "8",
            "--bays", "3",
        ]
    )
    assert "Auto services" in auto
    assert "not applied" in auto
    assert "Monthly:" in auto
    assert "Primary demand series: Google" in auto

    rest = run(
        [
            "--name", "48-Seat Bistro",
            "--location", "Austin, TX",
            "--industry", "full_service_restaurant",
            "--location-tier", "major_metro",
            "--google-reviews", "420",
            "--google-rating", "4.4",
            "--google-velocity", "18",
            "--yelp-reviews", "90",
            "--yelp-rating", "4.2",
            "--yelp-velocity", "3",
            "--seats", "48",
            "--ticket-low", "28",
            "--ticket-base", "42",
            "--ticket-high", "65",
            "--ticket-source", "menu",
        ]
    )
    assert "Full-service restaurant" in rest
    assert "source: menu" in rest
    # 48 seats * 2.2 turns * 26 days ≈ 2,746 tx/month ceiling
    assert "Capacity ceiling" in rest

    # Industry alias + no velocity should impute and stay Low or Medium, not crash
    sparse = run(
        [
            "--name", "New Dental",
            "--location", "Boise, ID",
            "--industry", "dentist",
            "--google-reviews", "12",
            "--google-rating", "5.0",
            "--years-open", "1",
        ]
    )
    assert "Dental" in sparse
    assert "imputed" in sparse.lower() or "imputed_from_age" in sparse

    # JSON format still parses
    import json as jsonlib
    raw = run(
        [
            "--format", "json",
            "--name", "X",
            "--location", "Y",
            "--industry", "qsr",
            "--google-reviews", "80",
            "--google-velocity", "10",
        ]
    )
    payload = jsonlib.loads(raw)
    assert payload["industry_key"] == "qsr"
    assert payload["primary_platform"] == "Google"
    assert payload["monthly_base"] > 0
    assert payload["rating_effect_applied"] is False

    print("ok")


if __name__ == "__main__":
    main()
