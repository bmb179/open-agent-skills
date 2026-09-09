#!/usr/bin/env python3
"""CLI for the review-revenue-estimator skill."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from model import Inputs, PlatformData, compute
from report import format_output, _ticket_from_args


def parse_args() -> tuple[Inputs, str]:
    parser = argparse.ArgumentParser(description="Review-based revenue estimator")
    parser.add_argument("--json", action="store_true", help="Read full JSON object from stdin")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--name", type=str)
    parser.add_argument("--location", type=str)
    parser.add_argument("--industry", type=str, default="default")
    parser.add_argument(
        "--location-tier",
        type=str,
        default="suburban",
        choices=["major_metro", "secondary_city", "suburban", "rural"],
    )
    parser.add_argument("--google-reviews", type=int, default=0)
    parser.add_argument("--google-rating", type=float, default=0.0)
    parser.add_argument("--google-velocity", type=float, default=0.0)
    parser.add_argument("--yelp-reviews", type=int, default=0)
    parser.add_argument("--yelp-rating", type=float, default=0.0)
    parser.add_argument("--yelp-velocity", type=float, default=0.0)
    parser.add_argument("--meta-reviews", type=int, default=0)
    parser.add_argument("--meta-rating", type=float, default=0.0)
    parser.add_argument("--meta-velocity", type=float, default=0.0)
    parser.add_argument("--aro-low", type=float)
    parser.add_argument("--aro-base", type=float)
    parser.add_argument("--aro-high", type=float)
    parser.add_argument("--ticket-low", type=float)
    parser.add_argument("--ticket-base", type=float)
    parser.add_argument("--ticket-high", type=float)
    parser.add_argument("--rate-low", type=float)
    parser.add_argument("--rate-base", type=float)
    parser.add_argument("--rate-high", type=float)
    parser.add_argument("--notes", type=str, default="")
    parser.add_argument("--years-open", type=float, default=0.0)
    parser.add_argument("--locations", type=int, default=1)
    parser.add_argument("--chain", action="store_true")
    parser.add_argument("--solicited", action="store_true")
    parser.add_argument("--seats", type=float, default=0.0)
    parser.add_argument("--rooms", type=float, default=0.0)
    parser.add_argument("--chairs", type=float, default=0.0)
    parser.add_argument("--bays", type=float, default=0.0)
    parser.add_argument("--crews", type=float, default=0.0)
    parser.add_argument("--days-open-month", type=float, default=26.0)
    parser.add_argument("--apply-rating-effect", action="store_true")
    parser.add_argument("--currency", type=str, default="USD")
    parser.add_argument("--ticket-source", type=str, default="industry_default")
    args = parser.parse_args()

    if args.json:
        data = json.load(sys.stdin)
        custom_ticket = None
        if "custom_ticket" in data:
            custom_ticket = tuple(data["custom_ticket"])
        elif "custom_aro" in data:
            custom_ticket = tuple(data["custom_aro"])
        inputs = Inputs(
            name=data["name"],
            location=data["location"],
            industry=data.get("industry", "default"),
            location_tier=data.get("location_tier", "suburban"),
            google=PlatformData(**data.get("google", {})),
            yelp=PlatformData(**data.get("yelp", {})),
            meta=PlatformData(**data.get("meta", {})),
            custom_ticket=custom_ticket,
            custom_review_rate=tuple(data["custom_review_rate"]) if "custom_review_rate" in data else None,
            notes=data.get("notes", ""),
            years_open=float(data.get("years_open", 0) or 0),
            locations=int(data.get("locations", 1) or 1),
            chain=bool(data.get("chain", False)),
            solicited=bool(data.get("solicited", False)),
            seats=float(data.get("seats", 0) or 0),
            rooms=float(data.get("rooms", 0) or 0),
            chairs=float(data.get("chairs", 0) or 0),
            bays=float(data.get("bays", 0) or 0),
            crews=float(data.get("crews", 0) or 0),
            days_open_month=float(data.get("days_open_month", 26) or 26),
            apply_rating_effect=bool(data.get("apply_rating_effect", False)),
            currency=data.get("currency", "USD"),
            ticket_source=data.get("ticket_source", "industry_default"),
        )
        return inputs, data.get("format", args.format)

    if not args.name or not args.location:
        parser.error("--name and --location are required (or use --json)")

    custom_rate = None
    if args.rate_low is not None and args.rate_base is not None and args.rate_high is not None:
        custom_rate = (args.rate_low, args.rate_base, args.rate_high)

    inputs = Inputs(
        name=args.name,
        location=args.location,
        industry=args.industry,
        location_tier=args.location_tier,
        google=PlatformData(args.google_reviews, args.google_rating, args.google_velocity),
        yelp=PlatformData(args.yelp_reviews, args.yelp_rating, args.yelp_velocity),
        meta=PlatformData(args.meta_reviews, args.meta_rating, args.meta_velocity),
        custom_ticket=_ticket_from_args(args),
        custom_review_rate=custom_rate,
        notes=args.notes,
        years_open=args.years_open,
        locations=args.locations,
        chain=args.chain,
        solicited=args.solicited,
        seats=args.seats,
        rooms=args.rooms,
        chairs=args.chairs,
        bays=args.bays,
        crews=args.crews,
        days_open_month=args.days_open_month,
        apply_rating_effect=args.apply_rating_effect,
        currency=args.currency,
        ticket_source=args.ticket_source,
    )
    return inputs, args.format


def main() -> None:
    inputs, fmt = parse_args()
    result = compute(inputs)
    if fmt == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
