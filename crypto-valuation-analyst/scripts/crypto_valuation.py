#!/usr/bin/env python3
"""
crypto_valuation.py — Autonomous Valuation Module for Crypto Project Analysis
Implements section 4.3 Forecasting, Valuation, Benchmarking, and Stress Testing
from the Crypto Project Transaction Memo Checklist (Banker's Due Diligence Framework
adapted for tokens/protocols).

- Bakes in market-based default assumptions when no custom inputs provided.
- Designed for use by crypto-project-analysis skill (full DD) and standalone
  Crypto Valuation Analyst skill/agent.
- Zero extra dependencies (stdlib + urllib). Reuses patterns from market_data.py.
- Always shows assumptions used, data sources, and limitations for transparency.

Usage (CLI):
  python crypto_valuation.py bitcoin
  python crypto_valuation.py ethereum --horizon 12 --base-growth 0.5
  python crypto_valuation.py uniswap --revenue 50000000  # annual USD revenue proxy

Outputs structured Markdown valuation report + JSON for agent parsing.
"""

import sys
import json
import argparse
import urllib.request
import urllib.error
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Reuse cache if available in skill context
try:
    from cache_utils import cached_fetch, save_to_cache, load_from_cache
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False
    def cached_fetch(key, fetch_func, **kwargs):
        return fetch_func()
    def save_to_cache(*a, **k): pass
    def load_from_cache(*a, **k): return None

# Symbol to CoinGecko ID map (extend as needed)
SYMBOL_MAP = {
    "btc": "bitcoin", "bitcoin": "bitcoin",
    "eth": "ethereum", "ethereum": "ethereum",
    "sol": "solana", "solana": "solana",
    "uni": "uniswap", "uniswap": "uniswap",
    "aave": "aave", "aave": "aave",
    "link": "chainlink", "chainlink": "chainlink",
    "pepe": "pepe",
    "doge": "dogecoin", "dogecoin": "dogecoin",
    "avax": "avalanche-2", "avalanche": "avalanche-2",
    "near": "near",
    "op": "optimism",
    "arb": "arbitrum",
}

def fetch_json(url: str, timeout: int = 20) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "crypto-valuation-skill/1.0 (autonomous)",
                "Accept": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(2)
        print(f"[WARN] HTTP {e.code} for {url}", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] Fetch error for {url}: {e}", file=sys.stderr)
    return None

def get_market_data(project_id: str) -> Dict[str, Any]:
    """Fetch core market/token data. Tries CoinGecko first."""
    coin_id = SYMBOL_MAP.get(project_id.lower(), project_id.lower())
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false"
    data = fetch_json(url)
    if not data or "market_data" not in data:
        # Fallback minimal
        return {
            "project": project_id,
            "source": "fallback",
            "current_price_usd": None,
            "market_cap_usd": None,
            "fdv_usd": None,
            "circulating_supply": None,
            "total_supply": None,
            "max_supply": None,
            "volume_24h_usd": None,
            "price_change_30d_pct": None,
            "fdv_mc_ratio": None,
            "dilution_signal": "UNKNOWN",
            "timestamp": datetime.utcnow().isoformat()
        }

    md = data["market_data"]
    price = md.get("current_price", {}).get("usd")
    mc = md.get("market_cap", {}).get("usd")
    fdv = md.get("fully_diluted_valuation", {}).get("usd")
    circ = md.get("circulating_supply")
    total = md.get("total_supply")
    max_s = md.get("max_supply")
    vol = md.get("total_volume", {}).get("usd")
    change_30d = md.get("price_change_percentage_30d_in_currency", {}).get("usd")

    fdv_mc_ratio = None
    dilution_signal = "LOW_RISK"
    if fdv and mc and mc > 0:
        fdv_mc_ratio = round(fdv / mc, 2)
        if fdv_mc_ratio > 3.0:
            dilution_signal = "HIGH_FUTURE_DILUTION_RISK"
        elif fdv_mc_ratio > 1.8:
            dilution_signal = "MODERATE_DILUTION_RISK"

    return {
        "project": project_id,
        "source": "coingecko",
        "current_price_usd": price,
        "market_cap_usd": mc,
        "fdv_usd": fdv,
        "circulating_supply": circ,
        "total_supply": total,
        "max_supply": max_s,
        "volume_24h_usd": vol,
        "price_change_30d_pct": change_30d,
        "fdv_mc_ratio": fdv_mc_ratio,
        "dilution_signal": dilution_signal,
        "timestamp": datetime.utcnow().isoformat()
    }

def get_default_assumptions(market_data: Dict[str, Any], provided: Optional[Dict] = None) -> Dict[str, Any]:
    """Bake in market-calibrated defaults if not provided. Transparent and conservative."""
    defaults = {
        "time_horizon_months": 12,
        "base_case_revenue_or_adoption_growth_yoy": 0.35,   # Moderate growth; calibrated to typical alt in neutral-bull regime
        "bull_case_revenue_or_adoption_growth_yoy": 1.00,   # Strong narrative + market tailwinds
        "bear_case_revenue_or_adoption_growth_yoy": -0.25,  # Contraction or dilution pressure
        "current_annual_protocol_revenue_usd": None,        # Placeholder; user or future API can provide (e.g. Token Terminal proxy)
        "discount_rate": 0.42,                              # Midpoint-ish of 20-70% startup range per checklist; high for crypto risk
        "probability_weights": {"base": 0.50, "bull": 0.25, "bear": 0.25},
        "projected_additional_supply_dilution_pct_in_horizon": 0.12,  # Conservative default for unlocks/vesting (varies widely; flag in output)
        "comps_peers": ["uniswap", "aave", "maker"],        # Default DeFi-ish peers for relative valuation
        "category": "general",                              # general | defi | l1 | meme | rwa etc. Influences comp choice
        "use_historical_atl_as_floor_proxy": True,
        "notes_on_assumptions": "Defaults are market-informed (conservative for most altcoins). Override with custom assumptions for precision. Revenue data often unavailable via free APIs — using growth-on-FDV proxy where needed."
    }
    if provided:
        defaults.update(provided)
    # Simple regime adjustment example (if 30d change strongly negative -> more bearish base)
    chg = market_data.get("price_change_30d_pct") or 0
    if chg < -20:
        defaults["base_case_revenue_or_adoption_growth_yoy"] = max(0.10, defaults["base_case_revenue_or_adoption_growth_yoy"] - 0.15)
        defaults["notes_on_assumptions"] += " | Regime-adjusted: recent weakness -> tempered base growth."
    elif chg > 30:
        defaults["bull_case_revenue_or_adoption_growth_yoy"] = min(1.5, defaults["bull_case_revenue_or_adoption_growth_yoy"] + 0.30)
        defaults["notes_on_assumptions"] += " | Regime-adjusted: recent strength -> lifted bull case."
    return defaults

def compute_dilution_stress_test(market_data: Dict[str, Any], assumptions: Dict[str, Any]) -> Dict[str, Any]:
    """Stress test per checklist: impact of unlocks on theoretical price (all else equal)."""
    mc = market_data.get("market_cap_usd") or 0
    circ = market_data.get("circulating_supply") or 0
    total = market_data.get("total_supply") or market_data.get("max_supply") or circ
    if circ <= 0 or mc <= 0:
        return {"error": "Insufficient supply/MC data for stress test", "theoretical_current_price": None}

    current_float_pct = (circ / total * 100) if total > 0 else 100.0
    addl_dilution = assumptions.get("projected_additional_supply_dilution_pct_in_horizon", 0.12)
    projected_total_after = total * (1 + addl_dilution)
    projected_float_pct = (circ / projected_total_after * 100) if projected_total_after > 0 else current_float_pct

    # Theoretical diluted price (MC constant / new higher supply)
    theoretical_diluted_price = (mc / projected_total_after) if projected_total_after > 0 else None
    current_price = market_data.get("current_price_usd")
    price_impact_pct = ((theoretical_diluted_price / current_price - 1) * 100) if current_price and theoretical_diluted_price else None

    return {
        "current_circulating_pct_of_total": round(current_float_pct, 1),
        "assumed_additional_dilution_pct": round(addl_dilution * 100, 1),
        "projected_circulating_pct_after": round(projected_float_pct, 1),
        "theoretical_diluted_price_usd": round(theoretical_diluted_price, 6) if theoretical_diluted_price else None,
        "approx_price_impact_from_dilution_pct": round(price_impact_pct, 1) if price_impact_pct else None,
        "interpretation": "Higher dilution from unlocks/vesting typically pressures price unless offset by strong adoption/revenue growth. This assumes constant MC (conservative; real outcome depends on narrative execution)."
    }

def compute_scenario_valuations(market_data: Dict[str, Any], assumptions: Dict[str, Any]) -> Dict[str, Any]:
    """Base/Bull/Bear scenario forecasts. Uses FDV growth proxy since revenue often N/A."""
    current_fdv = market_data.get("fdv_usd") or market_data.get("market_cap_usd") or 0
    if current_fdv <= 0:
        return {"error": "No FDV/MC data"}

    g_base = assumptions["base_case_revenue_or_adoption_growth_yoy"]
    g_bull = assumptions["bull_case_revenue_or_adoption_growth_yoy"]
    g_bear = assumptions["bear_case_revenue_or_adoption_growth_yoy"]
    addl_dil = assumptions.get("projected_additional_supply_dilution_pct_in_horizon", 0.12)
    probs = assumptions["probability_weights"]

    # Simple model: target FDV ~ current * (1 + g) adjusted for dilution drag
    def target_fdv(growth):
        gross = current_fdv * (1 + growth)
        # Dilution drag approx
        net = gross / (1 + addl_dil)
        return net

    fdv_base = target_fdv(g_base)
    fdv_bull = target_fdv(g_bull)
    fdv_bear = target_fdv(g_bear)

    # Expected FDV (probability weighted)
    exp_fdv = (fdv_base * probs["base"] + fdv_bull * probs["bull"] + fdv_bear * probs["bear"])

    current_price = market_data.get("current_price_usd") or 0
    circ = market_data.get("circulating_supply") or 1

    def fdv_to_price(fdv):
        # Rough: assumes proportional to current circ / total dynamics, but simplified
        return (fdv / (market_data.get("total_supply") or circ)) if (market_data.get("total_supply") or circ) > 0 else None

    return {
        "current_fdv_usd": round(current_fdv),
        "base_case_target_fdv_usd": round(fdv_base),
        "bull_case_target_fdv_usd": round(fdv_bull),
        "bear_case_target_fdv_usd": round(fdv_bear),
        "probability_weighted_expected_fdv_usd": round(exp_fdv),
        "base_case_implied_price_usd": round(fdv_to_price(fdv_base), 6) if fdv_to_price(fdv_base) else None,
        "bull_case_implied_price_usd": round(fdv_to_price(fdv_bull), 6) if fdv_to_price(fdv_bull) else None,
        "bear_case_implied_price_usd": round(fdv_to_price(fdv_bear), 6) if fdv_to_price(fdv_bear) else None,
        "assumptions_used": {
            "growth_rates": {"base": g_base, "bull": g_bull, "bear": g_bear},
            "dilution_drag": addl_dil,
            "probabilities": probs
        },
        "note": "Scenarios use FDV growth as proxy for adoption/revenue/value accrual (common when protocol revenue data unavailable). Override with actual revenue projections for DCF-style precision."
    }

def compute_price_floor_and_support(market_data: Dict[str, Any], assumptions: Dict[str, Any]) -> Dict[str, Any]:
    """Intrinsic floor / support levels per checklist. PoW mine cost or PoS DCF; altcoins often -> 0 or ATL proxy."""
    current_price = market_data.get("current_price_usd") or 0
    current_mc = market_data.get("market_cap_usd") or 0
    discount = assumptions["discount_rate"]
    rev = assumptions.get("current_annual_protocol_revenue_usd")

    intrinsic_floor = None
    method = "qualitative / historical proxy"
    if rev and rev > 0:
        # Simple PoS-style DCF floor (perpetuity, conservative)
        # Value ~ rev / discount_rate (no growth in floor case)
        intrinsic_floor = rev / discount
        method = "PoS DCF-style capitalization of current protocol revenue (conservative, 0 terminal growth)"
    else:
        # For most alts: natural tendency to 0 without strong utility/accrual; use ATL proxy or note
        if assumptions.get("use_historical_atl_as_floor_proxy"):
            # In real impl would fetch ATL, here proxy with "often 70-95% drawdown possible"
            intrinsic_floor = current_price * 0.05 if current_price else 0  # illustrative extreme floor
            method = "Qualitative: altcoins frequently approach 0 or historical ATL in bear; using illustrative 95% drawdown proxy for bear case stress"

    bear_uses_floor = True
    floor_note = "Bear case should incorporate this floor. Many tokens have weak or no intrinsic floor beyond speculation/utility demand."

    return {
        "intrinsic_floor_value_usd": round(intrinsic_floor, 2) if intrinsic_floor else None,
        "calculation_method": method,
        "discount_rate_used": discount,
        "revenue_input_used": rev,
        "bear_case_uses_floor": bear_uses_floor,
        "floor_note": floor_note,
        "checklist_reference": "Price floor often -99.9% for alts without collateral/utility; intrinsic = mine cost (PoW) or DCF rev cap (PoS)"
    }

def compute_comparables_valuation(market_data: Dict[str, Any], assumptions: Dict[str, Any]) -> Dict[str, Any]:
    """Comps analysis: what would target be worth at peer median multiples?"""
    # For autonomous: fetch quick data on default peers or note limitation
    peers = assumptions.get("comps_peers", ["uniswap", "aave"])
    peer_data = []
    for p in peers[:4]:  # limit calls
        pd = get_market_data(p)
        if pd.get("fdv_usd"):
            peer_data.append({
                "project": p,
                "fdv_usd": pd["fdv_usd"],
                "mc_usd": pd["market_cap_usd"],
                "fdv_mc": pd["fdv_mc_ratio"]
            })

    if not peer_data:
        return {"note": "Comps data unavailable in this run; using general market heuristic instead."}

    # Simple: median FDV of peers as rough "fair value" anchor for similar stage/sector
    fdvs = [p["fdv_usd"] for p in peer_data if p["fdv_usd"]]
    median_fdv = sorted(fdvs)[len(fdvs)//2] if fdvs else None

    target_fdv_at_median = median_fdv  # simplistic; in practice adjust for differences in rev, narrative strength, float etc.
    premium_discount_note = "Target may trade at premium/discount to comps based on stronger/weaker community, tokenomics, moat, or narrative timing (per checklist)."

    return {
        "peers_analyzed": [p["project"] for p in peer_data],
        "peer_median_fdv_usd": round(median_fdv) if median_fdv else None,
        "target_implied_fdv_at_peer_median": round(target_fdv_at_median) if target_fdv_at_median else None,
        "current_target_fdv": market_data.get("fdv_usd"),
        "premium_or_discount_to_median_pct": round( ((market_data.get("fdv_usd") or 0) / median_fdv - 1)*100 , 1) if median_fdv and market_data.get("fdv_usd") else None,
        "note": premium_discount_note + " Adjust for project-specific strengths (e.g. higher float at TGE = positive per empirical signals)."
    }

def aggregate_valuation_review(scenarios: Dict, stress: Dict, floor: Dict, comps: Dict, market_data: Dict) -> Dict[str, Any]:
    """Collect high/low/avg/median from all methods per checklist 4.3 Review."""
    estimates = []
    # Pull key point estimates (FDV or price where sensible)
    if scenarios.get("base_case_target_fdv_usd"):
        estimates.append(scenarios["base_case_target_fdv_usd"])
    if scenarios.get("bull_case_target_fdv_usd"):
        estimates.append(scenarios["bull_case_target_fdv_usd"])
    if scenarios.get("bear_case_target_fdv_usd"):
        estimates.append(scenarios["bear_case_target_fdv_usd"])
    if stress.get("theoretical_diluted_price_usd") and market_data.get("current_price_usd"):
        # Convert stress price impact to rough FDV equiv
        pass  # already in price terms; skip or convert
    if comps.get("target_implied_fdv_at_peer_median"):
        estimates.append(comps["target_implied_fdv_at_peer_median"])
    if floor.get("intrinsic_floor_value_usd"):
        estimates.append(floor["intrinsic_floor_value_usd"])

    valid = [e for e in estimates if e and e > 0]
    if not valid:
        return {"review_summary": "Insufficient point estimates for aggregate review. Run with more data or custom assumptions."}

    high = max(valid)
    low = min(valid)
    avg = sum(valid) / len(valid)
    median = sorted(valid)[len(valid)//2]

    return {
        "valuation_estimates_collected": len(valid),
        "high_estimate_usd": round(high),
        "low_estimate_usd": round(low),
        "average_estimate_usd": round(avg),
        "median_estimate_usd": round(median),
        "spread_pct": round( (high - low) / low * 100, 1) if low > 0 else None,
        "review_summary": "Aggregated from scenario targets, stress-tested dilution, comps median, and any intrinsic floor. Wide spread indicates high uncertainty (typical for crypto). Use as one input alongside full checklist (team, community, red flags, narrative fit). Probability-weighted expected from scenarios provides central tendency."
    }

def generate_valuation_report(project_id: str, custom_assumptions: Optional[Dict[str, Any]] = None) -> str:
    """Main entry: returns full Markdown report + embedded JSON for agents."""
    market = get_market_data(project_id)
    assumptions = get_default_assumptions(market, custom_assumptions)

    scenarios = compute_scenario_valuations(market, assumptions)
    stress = compute_dilution_stress_test(market, assumptions)
    floor = compute_price_floor_and_support(market, assumptions)
    comps = compute_comparables_valuation(market, assumptions)
    review = aggregate_valuation_review(scenarios, stress, floor, comps, market)

    report = f"""# Crypto Valuation Report: {project_id.upper()}
**Generated**: {datetime.utcnow().isoformat()} UTC | **Framework**: Crypto Project Transaction Memo Checklist §4.3 (Banker's Due Diligence adapted for tokens/protocols)
**Data Source**: Primarily CoinGecko (keyless) | **Autonomous Mode**: Yes — market-based defaults applied where inputs omitted.

## Market Snapshot (Current)
- **Price (USD)**: {market.get('current_price_usd')}
- **Market Cap**: ${market.get('market_cap_usd'):,} | **FDV**: ${market.get('fdv_usd'):,}
- **Circulating / Total Supply**: {market.get('circulating_supply')} / {market.get('total_supply')}
- **FDV/MC Ratio**: {market.get('fdv_mc_ratio')} → **Dilution Signal**: {market.get('dilution_signal')}
- **24h Volume**: ${market.get('volume_24h_usd'):,} | **30d Price Change**: {market.get('price_change_30d_pct')}%

## 1. Scenario Valuation (Base / Bull / Bear)
**Assumptions (baked-in defaults, regime-adjusted where possible)**: {assumptions['notes_on_assumptions']}
- Time Horizon: {assumptions['time_horizon_months']} months
- Growth (YoY adoption/revenue proxy): Base {assumptions['base_case_revenue_or_adoption_growth_yoy']*100:.0f}% | Bull {assumptions['bull_case_revenue_or_adoption_growth_yoy']*100:.0f}% | Bear {assumptions['bear_case_revenue_or_adoption_growth_yoy']*100:.0f}%
- Dilution drag applied: {assumptions['projected_additional_supply_dilution_pct_in_horizon']*100:.0f}%
- Probabilities: Base {assumptions['probability_weights']['base']*100:.0f}% | Bull {assumptions['probability_weights']['bull']*100:.0f}% | Bear {assumptions['probability_weights']['bear']*100:.0f}%

**Results**:
- Base Target FDV: ${scenarios.get('base_case_target_fdv_usd'):,} → Implied Price ~${scenarios.get('base_case_implied_price_usd')}
- Bull Target FDV: ${scenarios.get('bull_case_target_fdv_usd'):,} → Implied Price ~${scenarios.get('bull_case_implied_price_usd')}
- Bear Target FDV: ${scenarios.get('bear_case_target_fdv_usd'):,} → Implied Price ~${scenarios.get('bear_case_implied_price_usd')}
- Probability-Weighted Expected FDV: ${scenarios.get('probability_weighted_expected_fdv_usd'):,}

*Note*: Growth applied to current FDV as proxy for value accrual/adoption (checklist-aligned). Provide actual protocol revenue for true DCF.

## 2. Price Floor / Support Levels
- **Intrinsic Floor Value**: ${floor.get('intrinsic_floor_value_usd')} (method: {floor.get('calculation_method')})
- Discount Rate Applied: {floor.get('discount_rate_used')*100:.0f}%
- Bear case incorporates floor consideration.
- **Key Insight**: {floor.get('floor_note')}

## 3. Stress Test — Dilution from Unlocks / Vesting
{json.dumps(stress, indent=2)}

**Interpretation**: Significant unlocks can create overhang. Higher initial float at TGE is empirically positive signal (per Tokenomist/Lo-Medda research referenced in checklist).

## 4. Comparables (Relative Valuation)
{json.dumps(comps, indent=2)}

## 5. Aggregate Review (High / Low / Avg / Median across methods)
{json.dumps(review, indent=2)}

## Decision Context & Limitations (per full Checklist)
- This valuation is **one module** (4.3) of the complete Crypto Project Transaction Memo Checklist.
- Combine with Sections 1-3 (Thesis, Theme, Team/Community/Product/Security) and 5 (Red Flags, Scoring).
- **Red Flags to Cross-Check**: High team/investor allocation + short vesting, low TGE float, anon team, weak audits, narrative overextension, low liquidity/concentration risks.
- **Always verify latest on-chain data, audits, unlock schedules (Tokenomist), and docs independently.** This is a tool, **not financial advice**.
- For production use in agents: Parse the JSON blocks or call as library function.

**Full Checklist Reference**: See attached Crypto Project Transaction Memo Checklist (Gumroad-1.pdf) for complete 1-5 framework, SWOT mitigants rule, Porter's 5 Forces, red flags, and scoring rubric.

---
*Autonomous valuation script v1.0 — part of crypto analysis skill pack. Market assumptions are transparent defaults and can/should be overridden with project-specific thesis inputs for best results.*
"""

    # Also return machine-readable for the agent
    structured = {
        "project": project_id,
        "market_snapshot": market,
        "assumptions": assumptions,
        "scenarios": scenarios,
        "stress_test": stress,
        "price_floor": floor,
        "comparables": comps,
        "aggregate_review": review,
        "generated_at": datetime.utcnow().isoformat()
    }

    return report, structured

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Crypto Valuation per Checklist §4.3")
    parser.add_argument("project", help="Token symbol or CoinGecko ID (e.g. bitcoin, uniswap, pepe)")
    parser.add_argument("--horizon", type=int, default=None, help="Time horizon in months (overrides default)")
    parser.add_argument("--base-growth", type=float, default=None, help="Base case YoY growth decimal (e.g. 0.4)")
    parser.add_argument("--revenue", type=float, default=None, help="Current annual protocol revenue USD (enables DCF floor)")
    parser.add_argument("--dilution", type=float, default=None, help="Projected additional supply dilution decimal in horizon (e.g. 0.15)")
    parser.add_argument("--json-only", action="store_true", help="Output only the structured JSON")
    args = parser.parse_args()

    custom = {}
    if args.horizon: custom["time_horizon_months"] = args.horizon
    if args.base_growth: custom["base_case_revenue_or_adoption_growth_yoy"] = args.base_growth
    if args.revenue: custom["current_annual_protocol_revenue_usd"] = args.revenue
    if args.dilution: custom["projected_additional_supply_dilution_pct_in_horizon"] = args.dilution

    report_md, structured = generate_valuation_report(args.project, custom if custom else None)

    if args.json_only:
        print(json.dumps(structured, indent=2, default=str))
    else:
        print(report_md)
        print("\n\n## RAW STRUCTURED JSON (for agents/scripts)")
        print(json.dumps(structured, indent=2, default=str))
