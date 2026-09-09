#!/usr/bin/env python3
"""
onchain_bitcoin.py — Bitcoin on-chain data (fees, mempool, basic stats) keyless
Part of crypto-project-analysis skill. Feeds Section 4 quantitative + risk flags
in the Crypto Project Analysis Checklist.

Sources: btcnode.uk (free endpoints where available), Mempool.space public API,
BitcoinCharts (where keyless).

Usage:
  python onchain_bitcoin.py fees
  python onchain_bitcoin.py mempool
  python onchain_bitcoin.py stats
"""

import sys
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

# Cache support (graceful fallback)
try:
    from cache_utils import cached_fetch, load_from_cache
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False
    def cached_fetch(key, fetch_func, **kwargs): return fetch_func()
    def load_from_cache(*a, **k): return None

def fetch_json(url: str, timeout: int = 12) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "crypto-project-analysis/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[WARN] {url}: {e}", file=sys.stderr)
        return None

def get_fees() -> Dict[str, Any]:
    cache_key = "bitcoin_fees"

    def _live():
        data = fetch_json("https://mempool.space/api/v1/fees/recommended")
        if data:
            return {
                "source": "mempool.space",
                "fastestFee": data.get("fastestFee"),
                "halfHourFee": data.get("halfHourFee"),
                "hourFee": data.get("hourFee"),
                "economyFee": data.get("economyFee"),
                "minimumFee": data.get("minimumFee"),
                "checklist_note": "High fees often signal network congestion or strong on-chain demand. Use in macro context or BTC-related project analysis (Section 4)."
            }
        data = fetch_json("https://btcnode.uk/api/fee-estimates")
        if data:
            return {"source": "btcnode.uk", "data": data}
        return None

    if HAS_CACHE:
        result = cached_fetch(cache_key, _live, max_age_hours=2)  # fees change fast
        if result:
            return result
    else:
        result = _live()
        if result:
            return result

    # Final fallback to cache even if slightly stale
    if HAS_CACHE:
        cached = load_from_cache(cache_key, max_age_hours=48)
        if cached:
            return cached
    return {"error": "Could not fetch fee estimates from available sources."}

def get_mempool() -> Dict[str, Any]:
    cache_key = "bitcoin_mempool"

    def _live():
        data = fetch_json("https://mempool.space/api/mempool")
        if data:
            return {
                "source": "mempool.space",
                "count": data.get("count"),
                "vsize": data.get("vsize"),
                "total_fee": data.get("total_fee"),
                "fee_histogram": data.get("fee_histogram")[:5] if data.get("fee_histogram") else None,
            }
        return None

    if HAS_CACHE:
        result = cached_fetch(cache_key, _live, max_age_hours=1)
        if result:
            return result
    else:
        result = _live()
        if result:
            return result

    if HAS_CACHE:
        cached = load_from_cache(cache_key, max_age_hours=24)
        if cached:
            return cached
    return {"error": "Mempool data unavailable."}

def get_basic_stats() -> Dict[str, Any]:
    cache_key = "bitcoin_stats"

    def _live():
        data = fetch_json("https://mempool.space/api/blocks/tip/height")
        height = data if isinstance(data, int) else None
        hashrate_data = fetch_json("https://btcnode.uk/api/hashrate")
        hashrate = hashrate_data.get("current_hashrate") if hashrate_data else None
        return {
            "source": "mempool.space + btcnode.uk",
            "block_height": height,
            "estimated_hashrate": hashrate,
        }

    if HAS_CACHE:
        result = cached_fetch(cache_key, _live, max_age_hours=6)
        if result:
            return result
    else:
        result = _live()
        if result:
            return result

    if HAS_CACHE:
        cached = load_from_cache(cache_key, max_age_hours=48)
        if cached:
            return cached
    return {"error": "Could not fetch basic Bitcoin stats."}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python onchain_bitcoin.py [fees | mempool | stats] [--offline]")
        print("  --offline   Use cached data only (no live API calls)")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    offline = "--offline" in sys.argv

    if cmd == "fees":
        print(json.dumps(get_fees(), indent=2))
    elif cmd == "mempool":
        print(json.dumps(get_mempool(), indent=2))
    elif cmd == "stats":
        print(json.dumps(get_basic_stats(), indent=2))
    else:
        print(json.dumps({"error": "Unknown command. Use fees, mempool or stats."}, indent=2))
