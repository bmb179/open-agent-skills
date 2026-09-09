#!/usr/bin/env python3
"""
dex_stats.py — DEX liquidity and pool stats via free keyless APIs (0x + 1inch)
Part of crypto-project-analysis skill. Supports Section 4.1 liquidity depth
and risk flags in the Crypto Project Analysis Checklist.

Usage examples:
  python dex_stats.py 0x6982508145454ce325ddbe47a25d4ec3d2311933 ethereum   # PEPE on ETH
  python dex_stats.py So11111111111111111111111111111111111111112 solana   # SOL wrapped

Note: 0x and 1inch free tiers have limits and some endpoints evolved; script uses
public quote/liquidity where available and falls back gracefully.
"""

import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

try:
    from cache_utils import cached_fetch, load_from_cache
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False
    def cached_fetch(key, fetch_func, **kwargs): return fetch_func()
    def load_from_cache(*a, **k): return None

def fetch_json(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "crypto-project-analysis-skill/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[WARN] {url}: {e}", file=sys.stderr)
    return None

def get_0x_liquidity(token_address: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
    """0x API token/pool stats (free tier where available)."""
    # 0x has /swap/v1/quote for price/liquidity signals and /token/v1/tokens for metadata
    # Simpler: use a public liquidity estimate via quote for small size
    base_url = "https://api.0x.org"
    # Example: quote for 1 unit of token vs USDC or ETH to gauge depth
    params = {
        "sellToken": token_address,
        "buyToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" if chain == "ethereum" else "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        "sellAmount": "1000000000000000000"  # 1 token (adjust decimals in real use)
    }
    url = f"{base_url}/swap/v1/quote?{urllib.parse.urlencode(params)}"
    data = fetch_json(url)
    if data and "liquidityAvailable" in data:
        return {
            "source": "0x",
            "liquidity_available": data.get("liquidityAvailable"),
            "estimated_price": data.get("price"),
            "sources": data.get("sources", []),
            "checklist_note": "Liquidity signal from 0x aggregator. Low availability or high slippage on small size = warning for Section 4.1 and risk flags. Cross-check with actual DEX depth."
        }
    return None

def get_1inch_quote(token_address: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
    """1inch API quote as liquidity proxy (free keyless where supported)."""
    # 1inch has /v5.0/{chain}/quote
    chain_id_map = {"ethereum": 1, "polygon": 137, "arbitrum": 42161, "optimism": 10, "base": 8453}
    chain_id = chain_id_map.get(chain.lower(), 1)
    url = f"https://api.1inch.dev/swap/v5.0/{chain_id}/quote?fromTokenAddress={token_address}&toTokenAddress=0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48&amount=1000000000000000000"
    # Note: 1inch now often requires auth header for /dev, but public /v5 may work in some regions or older.
    # Fallback graceful
    data = fetch_json(url)
    if data and "toTokenAmount" in data:
        return {
            "source": "1inch",
            "to_amount": data.get("toTokenAmount"),
            "protocols": data.get("protocols", []),
            "checklist_note": "1inch quote gives execution price/liquidity hint. Use alongside 0x for multi-DEX view of depth and slippage risk."
        }
    return {"note": "1inch quote may require API key in current setup; falling back to manual DEX explorer check recommended."}

def get_dex_stats(token_address: str, chain: str = "ethereum") -> Dict[str, Any]:
    result = {"token_address": token_address, "chain": chain}
    ox = get_0x_liquidity(token_address, chain)
    if ox:
        result["0x"] = ox
    one = get_1inch_quote(token_address, chain)
    if one:
        result["1inch"] = one

    if not ox and not one:
        result["note"] = "No automated liquidity data returned. Manually check DexScreener, Birdeye (Solana), or DexTools for depth and top pools. Low liquidity is a key red flag in the checklist."
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dex_stats.py <token_contract_address> [chain=ethereum|solana|...] [--offline]")
        print("Example: python dex_stats.py 0x6982508145454ce325ddbe47a25d4ec3d2311933 ethereum")
        sys.exit(1)

    token = sys.argv[1]
    chain = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "ethereum"
    offline = "--offline" in sys.argv

    data = get_dex_stats(token, chain)
    if offline and HAS_CACHE:
        cache_key = f"dex_{token}_{chain}"
        cached = load_from_cache(cache_key, max_age_hours=48)
        if cached:
            data = cached
            data["_cache_mode"] = "offline_only"
    print(json.dumps(data, indent=2))
