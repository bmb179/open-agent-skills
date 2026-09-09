---
name: crypto-valuation-analyst
description: Performs crypto token and protocol valuation strictly following section 4.3 Forecasting, Valuation, Benchmarking, and Stress Testing of the Crypto Project Transaction Memo Checklist. Always executes every method listed: Scenario Valuation (Base/Bull/Bear with explicit assumptions and probability weights), Price Floors/Support Levels (including intrinsic DCF-style or proxy), Stress Test for dilution from unlocks, Comparables Analysis, Correlation testing (BTC/ETH, tech stocks, commodities), and Review (high/low/average/median across all outputs). Uses crypto_valuation.py which applies transparent market-based default assumptions when the user provides no custom inputs. Outputs a complete structured report covering all 4.3 elements plus the final aggregate review. Scope is limited to native crypto tokens and on-chain projects.
---

# Crypto Valuation Analyst

## Purpose
This skill completes a full valuation for a crypto token or protocol by executing **exactly** the methods in section 4.3 Forecasting, Valuation, Benchmarking, and Stress Testing of `references/Crypto_Project_Transaction_Memo_Checklist.md` (the lossless markdown of the finalized Crypto Project Transaction Memo Checklist):

- **Scenario Valuation**
  - Forecast Base, Bull, and Bear cases within the chosen time horizon.
  - Use explicit assumptions for adoption, revenue, and unlock rate.
  - Test sensitivity by changing assumption variables.
  - Apply probability weights based on judged likelihood of each case.

- **Price Floors or Support Levels**
  - Account for the tendency of altcoins to approach zero without a strong floor (potentially -99.9%).
  - Consider value of any underlying collateral.
  - Calculate Intrinsic Price Floor: mining cost (PoW) or DCF-style capitalization of revenue (PoS).
  - Apply a discount rate in the startup range (20%–70%, depending on growth stage).
  - Ensure the Bear case incorporates the price floor.

- **Stress Test Analysis**
  - Model the price impact of dilution from team and investor unlocks.
  - Current Price = Market Cap / Float.
  - Theoretical Diluted Price = Market Cap / Projected Float After Unlocks (all other factors equal).

- **Comparables Analysis**
  - Select projects similar in growth stage, sector, and financial metrics (MC/FDV, Price/Revenue).
  - Assess premium or discount relative to the project’s narrative.
  - Compare community strength and cap table (token allocation/vesting/float).
  - Calculate what the target would be worth at the comp set average or median multiple.

- **Test Correlation**
  - Measure correlation with blue-chip cryptos (BTC, ETH).
  - Measure correlation with tech sector stocks (e.g. NASDAQ 100).
  - Measure correlation with commodities (Gold, Oil, Electricity).
  - Consider forecasting price as a percentage of another asset (e.g. Bitcoin as “digital gold”).
  - Evaluate whether observed correlations support hedging (e.g. allocating a portion of the position to Bitcoin downside instruments).

- **Review**
  - Compute and present the high, low, average, and median valuations drawn from the scenario results, price floors/support levels, stress-tested valuation, and comparables market-based valuation.

The skill always produces output that explicitly addresses every bullet above.

## When to Activate
Activate this skill whenever the user requests a valuation, scenario analysis, dilution stress test, comps-based valuation, or asks “what is [token] worth?” for a native crypto token or on-chain project. It is designed to run the complete 4.3 process in one pass.

**Scope**: Only native crypto tokens, protocols, DeFi applications, L1/L2 chains, and on-chain assets. It does not analyze public equities, ETFs, or traditional companies.

## How It Works
1. The user supplies a project identifier (symbol, name, or CoinGecko ID) and may optionally provide custom assumptions (time horizon, growth rates, revenue figures, unlock/dilution percentages, specific comps, etc.).
2. If no custom assumptions are given, the skill uses `crypto_valuation.py` which automatically applies transparent, market-calibrated defaults (growth rates adjusted for recent price action, discount rate in the 20–70% startup range, conservative dilution estimate, etc.). All defaults are clearly stated in the output.
3. The script fetches current market data (price, market cap, FDV, circulating/total supply, FDV/MC ratio, recent performance) and runs every 4.3 method listed above.
4. The skill returns a single, complete report containing:
   - Scenario Valuation results (Base / Bull / Bear) with assumptions, sensitivity notes, and probability-weighted outcome.
   - Price Floor / Support Level calculation and Bear-case integration.
   - Stress Test showing theoretical diluted price from unlocks.
   - Comparables valuation with premium/discount commentary.
   - Correlation observations and hedging considerations.
   - Final Review: high, low, average, and median valuations across all methods.

The output is structured so every required element from section 4.3 of `references/Crypto_Project_Transaction_Memo_Checklist.md` is explicitly covered. Use that markdown file as the source of truth for the required methods, assumptions, and review outputs.

## Usage
**In Grok**: Activate the skill by name or say “Run crypto valuation analyst on [project]” (add custom assumptions if desired).

**CLI (any Python environment with internet)**:
```bash
python scripts/crypto_valuation.py bitcoin
python scripts/crypto_valuation.py uniswap --revenue 85000000 --base-growth 0.55 --dilution 0.08 --horizon 12
python scripts/crypto_valuation.py pepe --json-only
```

**As a Python function** (for agents or scripts):
```python
from crypto_valuation import generate_valuation_report
report_md, structured_json = generate_valuation_report("solana", custom_assumptions_dict)
```

**Claude or other LLMs**: Provide the skill description, `references/Crypto_Project_Transaction_Memo_Checklist.md` (§4.3), plus the `crypto_valuation.py` script. Instruct the model to execute the 4.3 methods using the script logic or equivalent calculations and to structure the final answer so every bullet in section 4.3 is addressed.

**Local agent frameworks** (LangGraph, CrewAI, etc.): Add as a tool node that calls the Python script or imports `generate_valuation_report`. Pass the project identifier and any user-supplied assumptions from upstream nodes. Consume the structured JSON for further processing.

## Output Requirements
The final response must contain clear sections or headings that map directly to the six elements of section 4.3:
- Scenario Valuation
- Price Floors or Support Levels
- Stress Test Analysis
- Comparables Analysis
- Test Correlation
- Review (high / low / average / median)

All assumptions (defaulted or user-provided) must be stated explicitly. The report must note data sources and remind the user to verify the latest on-chain data, unlock schedules, and project documentation independently.

**Always verify the latest on-chain data, audits, and documentation independently. This is a tool, not financial advice.**
