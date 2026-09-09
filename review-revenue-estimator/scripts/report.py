#!/usr/bin/env python3
"""Text/JSON report formatting for review-revenue-estimator."""
from __future__ import annotations

from typing import Any, Optional


def fmt_money(n: float, currency: str = "USD") -> str:
    symbol = "$" if currency in ("USD", "CAD", "AUD", "NZD") else ""
    prefix = "" if symbol else f"{currency} "
    if abs(n) >= 1_000_000:
        return f"{prefix}{symbol}{n/1_000_000:.2f}M"
    return f"{prefix}{symbol}{n:,.0f}"


def format_output(r: dict[str, Any]) -> str:
    lines = [
        f"**Business:** {r['name']} — {r['location']}",
        f"**Industry classification:** {r['industry_label']} (`{r['industry_key']}`)",
    ]
    if r["locations"] > 1:
        lines.append(f"**Locations in estimate:** {r['locations']}")
    lines.append("")
    lines.append("**Data gathered:**")
    g, y, m = r["google"], r["yelp"], r["meta"]

    def plat_line(label: str, p: dict, used_vel: float) -> str:
        rating = f"{p['rating']:.1f}★" if p["rating"] > 0 else "n/a"
        if p["velocity"] and p["velocity"] > 0:
            vel = f"~{p['velocity']:.1f}/month (observed)"
        elif p["reviews"] > 0:
            vel = f"~{used_vel:.1f}/month (imputed)"
        else:
            vel = "no presence / no usable count"
        return f"- {label}: {p['reviews']} reviews, {rating}, {vel}"

    lines.append(plat_line("Google", g, r["google_velocity_used"]))
    lines.append(plat_line("Yelp", y, r["yelp_velocity_used"]))
    lines.append(plat_line("Meta", m, r["meta_velocity_used"]))
    lines.append(
        f"- Primary demand series: {r['primary_platform']} "
        f"({r['primary_velocity']:.1f}/month, {r['velocity_source']})"
    )
    lines.append("")
    lines.append("**Key assumptions:**")
    rr = r["review_rates"]
    lines.append(
        f"- Review rate (share of transactions that produce a primary-platform review): "
        f"{rr[0]*100:.1f}–{rr[2]*100:.1f}% (base {rr[1]*100:.1f}%)"
    )
    tk = r["tickets"]
    lines.append(
        f"- Average ticket: {fmt_money(tk[0], r['currency'])}–{fmt_money(tk[2], r['currency'])} "
        f"(base {fmt_money(tk[1], r['currency'])}; source: {r['ticket_source']})"
    )
    lines.append(
        f"- Location ticket adjustment: {r['loc_ticket_mult']:.2f}×; "
        f"review-rate adjustment: {r['loc_rate_mult']:.2f}×"
    )
    if r["rating_effect_applied"]:
        lines.append(
            f"- Rating multiplier (counterfactual, Luca-style): {r['rating_mult']:.2f}× "
            f"(avg {r['avg_rating']})"
        )
    else:
        lines.append(
            f"- Rating multiplier: not applied (avg rating {r['avg_rating'] or 'n/a'}). "
            "Velocity already embeds realized demand."
        )
    lines.append(
        f"- Implied base throughput: ~{r['implied_tx_month_base']:,} transactions/month "
        f"(~{r['implied_tx_day_base']}/open day)"
    )
    if r["capacity_desc"]:
        cap = r["capacity_tx_month"]
        hit = " — HIGH CASE CLAMPED" if r["capacity_hit"] else ""
        lines.append(f"- Capacity ceiling: ~{cap:,.0f} tx/month ({r['capacity_desc']}){hit}")
    flags = []
    if r["chain"]:
        flags.append("chain")
    if r["solicited"]:
        flags.append("review-solicitation observed")
    if r["years_open"]:
        flags.append(f"{r['years_open']:g} years open")
    if flags:
        lines.append(f"- Flags: {', '.join(flags)}")
    if r["notes"]:
        lines.append(f"- Notes: {r['notes']}")
    lines.append(f"- Model: {r['model']}")
    lines.append("")
    lines.append("**Revenue estimate:**")
    lines.append(
        f"- Monthly: {fmt_money(r['monthly_low'], r['currency'])} – "
        f"{fmt_money(r['monthly_high'], r['currency'])} "
        f"(base {fmt_money(r['monthly_base'], r['currency'])})"
    )
    lines.append(
        f"- Annual: {fmt_money(r['annual_low'], r['currency'])} – "
        f"{fmt_money(r['annual_high'], r['currency'])} "
        f"(base {fmt_money(r['annual_base'], r['currency'])})"
    )
    lines.append("")
    lines.append(f"**Confidence:** {r['confidence']} — {r['conf_reason']}")
    lines.append("")
    lines.append(
        "**Caveats:** Proxy from public review flow and industry ticket priors, not audited sales. "
        "Offline/contract/B2B revenue, delivery mix, seasonality, review gating, fake or solicited "
        "reviews, and multi-location pins the scrape missed can all move the true number outside this range. "
        "Womply (2019) finds review count correlates with revenue more than star rating; Luca (2011) "
        "5–9% per star is a causal effect for independent restaurants and is not added on top of velocity "
        "unless --apply-rating-effect is set."
    )
    return "\n".join(lines)


def _ticket_from_args(args) -> Optional[tuple[float, float, float]]:
    t_low = args.ticket_low if args.ticket_low is not None else args.aro_low
    t_base = args.ticket_base if args.ticket_base is not None else args.aro_base
    t_high = args.ticket_high if args.ticket_high is not None else args.aro_high
    if t_low is not None and t_base is not None and t_high is not None:
        return (t_low, t_base, t_high)
    return None
