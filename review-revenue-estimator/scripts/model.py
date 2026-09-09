#!/usr/bin/env python3
"""Core volume identity for review-revenue-estimator."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from defaults import ALIASES, INDUSTRY_DEFAULTS, LOCATION_ADJUST


@dataclass
class PlatformData:
    reviews: int = 0
    rating: float = 0.0
    velocity: float = 0.0


@dataclass
class Inputs:
    name: str
    location: str
    industry: str = "default"
    location_tier: str = "suburban"
    google: PlatformData = field(default_factory=PlatformData)
    yelp: PlatformData = field(default_factory=PlatformData)
    meta: PlatformData = field(default_factory=PlatformData)
    custom_ticket: Optional[tuple[float, float, float]] = None
    custom_review_rate: Optional[tuple[float, float, float]] = None
    notes: str = ""
    years_open: float = 0.0
    locations: int = 1
    chain: bool = False
    solicited: bool = False
    seats: float = 0.0
    rooms: float = 0.0
    chairs: float = 0.0
    bays: float = 0.0
    crews: float = 0.0
    days_open_month: float = 26.0
    apply_rating_effect: bool = False
    currency: str = "USD"
    ticket_source: str = "industry_default"


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def resolve_industry(raw: str) -> tuple[str, dict[str, Any]]:
    key = raw.lower().strip().replace(" ", "_").replace("-", "_")
    if key in INDUSTRY_DEFAULTS:
        return key, INDUSTRY_DEFAULTS[key]
    if key in ALIASES:
        mapped = ALIASES[key]
        return mapped, INDUSTRY_DEFAULTS[mapped]
    return "default", INDUSTRY_DEFAULTS["default"]


def platform_velocity(p: PlatformData, years_open: float) -> tuple[float, str]:
    if p.velocity and p.velocity > 0:
        return float(p.velocity), "observed"
    if p.reviews <= 0:
        return 0.0, "none"
    if years_open and years_open > 0:
        years = max(0.5, float(years_open))
        effective_years = min(years, 4.0)
        return p.reviews / (effective_years * 12.0), "imputed_from_age"
    return p.reviews / 48.0, "imputed_no_age"


def weighted_rating(platforms: list[PlatformData]) -> float:
    w = 0.0
    n = 0.0
    for p in platforms:
        if p.reviews > 0 and p.rating > 0:
            w += p.rating * p.reviews
            n += p.reviews
    return (w / n) if n > 0 else 0.0


def capacity_monthly_tx(inputs: Inputs, ind: dict[str, Any]) -> tuple[Optional[float], str]:
    turns = ind.get("turns_per_day")
    days = inputs.days_open_month or 26.0
    if inputs.seats and inputs.seats > 0:
        t = turns if turns else 2.5
        return inputs.seats * t * days, f"{inputs.seats:.0f} seats × {t:g} turns/day × {days:g} days"
    if inputs.rooms and inputs.rooms > 0:
        return inputs.rooms * 30.0 * 0.85, f"{inputs.rooms:.0f} rooms × 30d × 0.85 occupancy cap"
    if inputs.chairs and inputs.chairs > 0:
        t = turns if turns else 6.0
        return inputs.chairs * t * days, f"{inputs.chairs:.0f} chairs × {t:g} clients/day × {days:g} days"
    if inputs.bays and inputs.bays > 0:
        t = turns if turns else 3.0
        return inputs.bays * t * days, f"{inputs.bays:.0f} bays × {t:g} jobs/day × {days:g} days"
    if inputs.crews and inputs.crews > 0:
        t = turns if turns else 2.5
        return inputs.crews * t * days, f"{inputs.crews:.0f} crews × {t:g} jobs/day × {days:g} days"
    return None, ""


def compute(inputs: Inputs) -> dict[str, Any]:
    ind_key, ind = resolve_industry(inputs.industry)
    loc = LOCATION_ADJUST.get(inputs.location_tier, LOCATION_ADJUST["suburban"])

    rates = list(inputs.custom_review_rate or ind["review_rate"])
    tickets = list(inputs.custom_ticket or ind["ticket"])
    ticket_source = inputs.ticket_source
    if inputs.custom_ticket:
        ticket_source = inputs.ticket_source if inputs.ticket_source != "industry_default" else "custom_override"

    if inputs.solicited and not inputs.custom_review_rate:
        rates = [rates[0] * 1.15, rates[1] * 1.25, min(0.35, rates[2] * 1.35)]

    if inputs.chain and not inputs.custom_review_rate:
        rates = [r * 1.15 for r in rates]

    rates = [clamp(r * loc["rate"], 0.002, 0.40) for r in rates]
    ticket_mult = loc["ticket"]

    g_vel, g_src = platform_velocity(inputs.google, inputs.years_open)
    y_vel, y_src = platform_velocity(inputs.yelp, inputs.years_open)
    m_vel, m_src = platform_velocity(inputs.meta, inputs.years_open)

    if g_vel > 0:
        primary_vel, primary_src, primary_name = g_vel, f"google_{g_src}", "Google"
    elif y_vel > 0:
        primary_vel, primary_src, primary_name = y_vel, f"yelp_{y_src}", "Yelp"
    elif m_vel > 0:
        primary_vel, primary_src, primary_name = m_vel, f"meta_{m_src}", "Meta"
    else:
        primary_vel, primary_src, primary_name = 0.0, "none", "none"

    velocity_imputed = "imputed" in primary_src
    avg_rating = weighted_rating([inputs.google, inputs.yelp, inputs.meta])

    rating_mult = 1.0
    if inputs.apply_rating_effect and avg_rating > 0 and not inputs.chain:
        rating_mult = clamp(1.0 + (avg_rating - 4.1) * 0.06, 0.85, 1.20)

    loc_count = max(1, int(inputs.locations or 1))

    def scenario(rate: float, ticket: float, vel_factor: float) -> dict[str, float]:
        vel = primary_vel * vel_factor
        tx = (vel / rate) if rate > 0 else 0.0
        monthly = tx * ticket * ticket_mult * rating_mult
        return {"velocity": vel, "transactions": tx, "monthly": monthly, "annual": monthly * 12.0}

    low = scenario(rates[2], tickets[0], 0.85)
    base = scenario(rates[1], tickets[1], 1.00)
    high = scenario(rates[0], tickets[2], 1.20)

    cap_tx, cap_desc = capacity_monthly_tx(inputs, ind)
    capacity_hit = False
    if cap_tx and cap_tx > 0:
        cap_tx_total = cap_tx * loc_count
        for sc in (low, base, high):
            if sc["transactions"] * loc_count > cap_tx_total * 1.05:
                capacity_hit = True
        if high["transactions"] * loc_count > cap_tx_total:
            for sc, ticket in ((base, tickets[1]), (high, tickets[2]), (low, tickets[0])):
                tx_system = sc["transactions"] * loc_count
                if tx_system > cap_tx_total:
                    sc["transactions"] = cap_tx_total / loc_count
                    sc["monthly"] = sc["transactions"] * ticket * ticket_mult * rating_mult
                    sc["annual"] = sc["monthly"] * 12.0

    if loc_count > 1:
        for sc in (low, base, high):
            sc["monthly"] *= loc_count
            sc["annual"] *= loc_count
            sc["transactions"] *= loc_count

    platforms_with_data = sum(1 for p in (inputs.google, inputs.yelp, inputs.meta) if p.reviews > 5)
    total_reviews = inputs.google.reviews + inputs.yelp.reviews + inputs.meta.reviews
    agreement = "n/a"
    if g_vel > 0 and y_vel > 0:
        if y_vel > g_vel * 1.25:
            agreement = "divergent"
        elif g_vel > y_vel * 12:
            agreement = "divergent"
        else:
            agreement = "aligned"

    reasons = []
    if platforms_with_data >= 2 and total_reviews >= 80 and primary_vel >= 3 and not velocity_imputed:
        confidence = "High"
        reasons.append("Multiple platforms, meaningful volume, observed recent velocity.")
    elif platforms_with_data >= 1 and total_reviews >= 30:
        confidence = "Medium"
        reasons.append("Primary platform usable but secondary data or velocity quality is limited.")
    else:
        confidence = "Low"
        reasons.append("Sparse reviews, single weak platform, or very low volume.")

    if velocity_imputed:
        if confidence == "High":
            confidence = "Medium"
        reasons.append("Velocity was imputed from lifetime count, not dated recent reviews.")
    if ticket_source == "industry_default":
        reasons.append("Ticket is a national prior, not a local menu/invoice override.")
    else:
        reasons.append(f"Ticket source: {ticket_source}.")
    if agreement == "divergent":
        if confidence == "High":
            confidence = "Medium"
        reasons.append("Google and Yelp velocities are inverted or extremely far apart.")
    if capacity_hit:
        if confidence == "High":
            confidence = "Medium"
        reasons.append("Implied demand hit a physical capacity ceiling; high case was clamped.")
    if inputs.chain:
        reasons.append("Chain flag set — rating effect suppressed; review rate nudged up.")
    if primary_name not in ("Google", "none"):
        reasons.append(f"Primary demand series is {primary_name}, not Google.")
    if primary_name == "none":
        confidence = "Low"
        reasons.append("No usable review velocity on any platform.")

    return {
        "name": inputs.name,
        "location": inputs.location,
        "industry_key": ind_key,
        "industry_label": ind["label"],
        "google": asdict(inputs.google),
        "yelp": asdict(inputs.yelp),
        "meta": asdict(inputs.meta),
        "primary_platform": primary_name,
        "primary_velocity": round(primary_vel, 2),
        "velocity_source": primary_src,
        "google_velocity_used": round(g_vel, 2),
        "yelp_velocity_used": round(y_vel, 2),
        "meta_velocity_used": round(m_vel, 2),
        "velocity_agreement": agreement,
        "avg_rating": round(avg_rating, 2) if avg_rating else 0.0,
        "review_rates": [round(r, 4) for r in rates],
        "tickets": tickets,
        "ticket_source": ticket_source,
        "loc_ticket_mult": loc["ticket"],
        "loc_rate_mult": loc["rate"],
        "rating_mult": round(rating_mult, 3),
        "rating_effect_applied": bool(inputs.apply_rating_effect and rating_mult != 1.0),
        "locations": loc_count,
        "chain": inputs.chain,
        "solicited": inputs.solicited,
        "years_open": inputs.years_open,
        "implied_tx_month_base": round(base["transactions"]),
        "implied_tx_day_base": round(base["transactions"] / max(inputs.days_open_month or 26.0, 1.0), 1),
        "capacity_tx_month": round(cap_tx * loc_count) if cap_tx else None,
        "capacity_desc": cap_desc or None,
        "capacity_hit": capacity_hit,
        "monthly_low": round(low["monthly"]),
        "monthly_base": round(base["monthly"]),
        "monthly_high": round(high["monthly"]),
        "annual_low": round(low["annual"]),
        "annual_base": round(base["annual"]),
        "annual_high": round(high["annual"]),
        "confidence": confidence,
        "conf_reason": " ".join(reasons),
        "currency": inputs.currency,
        "notes": inputs.notes,
        "model": (
            "monthly_tx = primary_velocity / review_rate; "
            "monthly_rev = monthly_tx × ticket × location_ticket_mult"
            + (" × rating_mult" if inputs.apply_rating_effect else "")
        ),
    }
