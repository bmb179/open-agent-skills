#!/usr/bin/env python3
"""
solana_rpc.py — Basic Solana on-chain queries via public JSON RPC (keyless)
Part of crypto-project-analysis skill. Useful for Solana projects in
Section 4 quantitative metrics and holder/usage signals.

Usage:
  python solana_rpc.py <mint_or_account> getTokenSupply
  python solana_rpc.py So11111111111111111111111111111111111111112 getAccountInfo
"""

import sys
import json
import urllib.request
from typing import Any, Dict, Optional

try:
    from cache_utils import cached_fetch, load_from_cache
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False
    def cached_fetch(key, fetch_func, **kwargs): return fetch_func()
    def load_from_cache(*a, **k): return None

SOLANA_RPC = "https://api.mainnet-beta.solana.com"

def rpc_call(method: str, params: list) -> Optional[Dict[str, Any]]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        SOLANA_RPC,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[WARN] Solana RPC {method}: {e}", file=sys.stderr)
        return None

def get_token_supply(mint: str) -> Dict[str, Any]:
    res = rpc_call("getTokenSupply", [mint])
    if res and "result" in res:
        val = res["result"]["value"]
        return {
            "source": "solana_rpc",
            "mint": mint,
            "amount": val.get("amount"),
            "decimals": val.get("decimals"),
            "uiAmount": val.get("uiAmount"),
            "uiAmountString": val.get("uiAmountString"),
            "checklist_note": "Circulating supply proxy for Solana tokens. Compare to total supply from market_data.py for FDV/MC and dilution signals in the checklist."
        }
    return {"error": "Could not retrieve token supply."}

def get_account_info(pubkey: str) -> Dict[str, Any]:
    res = rpc_call("getAccountInfo", [pubkey, {"encoding": "jsonParsed"}])
    if res and "result" in res and res["result"]:
        return {
            "source": "solana_rpc",
            "pubkey": pubkey,
            "lamports": res["result"]["value"].get("lamports"),
            "owner": res["result"]["value"].get("owner"),
            "data": res["result"]["value"].get("data"),
            "checklist_note": "Basic account state. For program accounts or large token accounts can give usage signals."
        }
    return {"error": "Account not found or RPC error."}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python solana_rpc.py <pubkey_or_mint> <getTokenSupply|getAccountInfo> [--offline]")
        sys.exit(1)

    target = sys.argv[1]
    method = sys.argv[2]
    offline = "--offline" in sys.argv

    if method == "getTokenSupply":
        data = get_token_supply(target)
    elif method == "getAccountInfo":
        data = get_account_info(target)
    else:
        data = {"error": "Unsupported method. Use getTokenSupply or getAccountInfo."}

    if offline and HAS_CACHE:
        cache_key = f"solana_{target}_{method}"
        cached = load_from_cache(cache_key, max_age_hours=48)
        if cached:
            data = cached
            data["_cache_mode"] = "offline_only"
    print(json.dumps(data, indent=2))
