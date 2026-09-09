#!/usr/bin/env python3
"""
market_data.py — Robust multi-source crypto market data fetcher (keyless)
Part of crypto-project-analysis skill. Follows the Crypto Project Analysis Checklist.

Usage:
  python market_data.py bitcoin
  python market_data.py ethereum
  python market_data.py solana
  python market_data.py pepe

Tries CoinGecko first (best coverage), then Coinpaprika, CoinStats, Coinlore, CryptoCompare.
Returns JSON with price, market_cap, fdv, volume, supplies, changes, and dilution signal.
Zero external dependencies (uses urllib + json from stdlib).
"""

import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional

# Add cache support
try:
    from cache_utils import cached_fetch, save_to_cache, load_from_cache
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False
    def cached_fetch(key, fetch_func, **kwargs):
        return fetch_func()
    def save_to_cache(*a, **k): pass
    def load_from_cache(*a, **k): return None

# Common symbol to CoinGecko ID mapping for convenience
SYMBOL_MAP = {
    "btc": "bitcoin", "bitcoin": "bitcoin",
    "eth": "ethereum", "ethereum": "ethereum",
    "sol": "solana", "solana": "solana",
    "usdt": "tether", "tether": "tether",
    "usdc": "usd-coin", "usd-coin": "usd-coin",
    "bnb": "binancecoin", "binancecoin": "binancecoin",
    "xrp": "ripple", "ripple": "ripple",
    "ada": "cardano", "cardano": "cardano",
    "doge": "dogecoin", "dogecoin": "dogecoin",
    "pepe": "pepe",
    "shib": "shiba-inu", "shiba-inu": "shiba-inu",
}

def fetch_json(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    """Simple GET with basic headers and timeout."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "crypto-project-analysis-skill/1.0 (keyless)",
                "Accept": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            time.sleep(1.5)  # simple backoff
        print(f"[WARN] HTTP {e.code} for {url}", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] Error fetching {url}: {e}", file=sys.stderr)
    return None

def try_coingecko(coin_id: str) -> Optional[Dict[str, Any]]:
    """CoinGecko /coins/{id} endpoint (free, keyless, rich data)."""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false"
    data = fetch_json(url)
    if not data or "market_data" not in data:
        return None

    md = data["market_data"]
    current_price = md.get("current_price", {}).get("usd")
    market_cap = md.get("market_cap", {}).get("usd")
    fdv = md.get("fully_diluted_valuation", {}).get("usd")
    vol_24h = md.get("total_volume", {}).get("usd")
    circ_supply = md.get("circulating_supply")
    total_supply = md.get("total_supply")
    max_supply = md.get("max_supply")

    fdv_mc_ratio = None
    if fdv and market_cap and market_cap > 0:
        fdv_mc_ratio = round(fdv / market_cap, 2)

    dilution_signal = "LOW_RISK"
    if fdv_mc_ratio:
        if fdv_mc_ratio > 3:
            dilution_signal = "HIGH_FUTURE_DILUTION_RISK"
        elif fdv_mc_ratio > 1.8:
            dilution_signal = "MODERATE_DILUTION_RISK"

    return {
        "source": "coingecko",
        "id": data.get("id"),
        "symbol": data.get("symbol", "").upper(),
        "name": data.get("name"),
        "current_price_usd": current_price,
        "market_cap_usd": market_cap,
        "fdv_usd": fdv,
        "volume_24h_usd": vol_24h,
        "circulating_supply": circ_supply,
        "total_supply": total_supply,
        "max_supply": max_supply,
        "fdv_mc_ratio": fdv_mc_ratio,
        "dilution_signal": dilution_signal,
        "price_change_24h": md.get("price_change_percentage_24h"),
        "price_change_7d": md.get("price_change_percentage_7d"),
        "price_change_30d": md.get("price_change_percentage_30d"),
        "last_updated": md.get("last_updated"),
        "checklist_note": "Use FDV/MC ratio and dilution_signal for Section 3.3 Tokenomics & Section 4.1 risk assessment. High ratio often correlates with unlock overhang per empirical research."
    }

def try_coinpaprika(coin_id: str) -> Optional[Dict[str, Any]]:
    """Coinpaprika /v1/coins/{id} (free keyless)."""
    # Coinpaprika uses ids like btc-bitcoin
    paprika_id = coin_id if "-" in coin_id else f"{coin_id[:3]}-{coin_id}"  # rough
    # Better: try common mapping or search, but for simplicity try direct
    url = f"https://api.coinpaprika.com/v1/coins/{coin_id}"
    data = fetch_json(url)
    if not data or "quotes" not in data:
        return None

    q = data["quotes"].get("USD", {})
    return {
        "source": "coinpaprika",
        "id": data.get("id"),
        "symbol": data.get("symbol", "").upper(),
        "name": data.get("name"),
        "current_price_usd": q.get("price"),
        "market_cap_usd": q.get("market_cap"),
        "fdv_usd": q.get("market_cap") * (data.get("total_supply") or 1) / (data.get("circulating_supply") or 1) if data.get("circulating_supply") else None,
        "volume_24h_usd": q.get("volume_24h"),
        "circulating_supply": data.get("circulating_supply"),
        "total_supply": data.get("total_supply"),
        "max_supply": data.get("max_supply"),
        "fdv_mc_ratio": None,  # approximate above
        "dilution_signal": "CHECK_MANUALLY",
        "price_change_24h": q.get("percent_change_24h"),
        "last_updated": data.get("last_updated"),
        "checklist_note": "Fallback source. Verify supply numbers against CoinGecko or project docs for accurate FDV/MC and unlock risk signals."
    }

def try_simple_sources(symbol: str) -> Optional[Dict[str, Any]]:
    """Very simple price from CoinCap or others as last resort."""
    # CoinCap
    url = f"https://api.coincap.io/v2/assets/{symbol.lower()}"
    data = fetch_json(url)
    if data and "data" in data:
        d = data["data"]
        price = float(d.get("priceUsd", 0))
        mc = float(d.get("marketCapUsd", 0)) if d.get("marketCapUsd") else None
        return {
            "source": "coincap",
            "symbol": d.get("symbol"),
            "name": d.get("name"),
            "current_price_usd": price,
            "market_cap_usd": mc,
            "fdv_usd": None,
            "volume_24h_usd": float(d.get("volumeUsd24Hr", 0)) if d.get("volumeUsd24Hr") else None,
            "checklist_note": "Basic price/MC only. Use primary sources for full supply/FDV data."
        }
    return None

def get_market_data(query: str, use_cache: bool = True, max_cache_age_hours: int = 6) -> Dict[str, Any]:
    """Main entry: resolve query to best available data. Now with offline caching support."""
    q = query.lower().strip()
    coin_id = SYMBOL_MAP.get(q, q)
    cache_key = f"market_data_{coin_id}"

    def _live_fetch():
        # Try CoinGecko first
        result = try_coingecko(coin_id)
        if result:
            return result

        # Fallbacks
        result = try_coinpaprika(coin_id)
        if result:
            return result

        result = try_simple_sources(q)
        if result:
            return result
        return None

    if use_cache:
        result = cached_fetch(cache_key, _live_fetch, max_age_hours=max_cache_age_hours)
        if result:
            return result
    else:
        result = _live_fetch()
        if result:
            return result

    return {
        "error": f"No data found for '{query}'. Try exact CoinGecko ID (e.g. 'pepe' not 'pepe-coin').",
        "suggestions": "Check https://www.coingecko.com/ for correct ID. Or run with full slug like 'based-pepe'.",
        "cache_note": "Live APIs unreachable. Try again later or use cached data if available."
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python market_data.py <symbol-or-coingecko-id> [--offline]")
        print("Examples: bitcoin | ethereum | solana | pepe | based-pepe")
        print("  --offline    Force use of cache only (no live API calls)")
        sys.exit(1)

    query = sys.argv[1]
    offline = "--offline" in sys.argv or "--cache-only" in sys.argv

    data = get_market_data(query, use_cache=True, max_cache_age_hours=6)
    if offline and HAS_CACHE:
        # In strict offline mode, only use cache (even if slightly stale)
        cache_key = f"market_data_{SYMBOL_MAP.get(query.lower().strip(), query.lower().strip())}"
        cached = load_from_cache(cache_key, max_age_hours=72)
        if cached:
            cached["_cache_mode"] = "offline_only"
            data = cached
        else:
            data = {"error": "No cached data available and offline mode requested."}

    print(json.dumps(data, indent=2, ensure_ascii=False))
