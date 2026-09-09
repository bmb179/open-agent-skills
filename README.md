# open-agent-skills

Public agent skills for Grok and other coding agents.

Each folder is a self-contained skill: `SKILL.md` plus optional `scripts/` and `references/`.

## Skills

### [crypto-project-analysis](crypto-project-analysis/)
Autonomous due diligence for **native crypto tokens, protocols, DeFi apps, and L1/L2 chains**. Follows the Crypto Project Transaction Memo Checklist. Uses free keyless APIs (CoinGecko, Coinpaprika, Solana RPC, mempool, GitHub) and shows full work. Does **not** analyze public equities, ETFs, or mining stocks.

```bash
python crypto-project-analysis/scripts/market_data.py solana
python crypto-project-analysis/scripts/crypto_valuation.py uniswap
```

### [crypto-valuation-analyst](crypto-valuation-analyst/)
Runs every method in checklist §4.3: scenario valuation (base/bull/bear), price floors, unlock dilution stress test, comparables, correlation notes, and a high/low/average/median review.

```bash
python crypto-valuation-analyst/scripts/crypto_valuation.py bitcoin
python crypto-valuation-analyst/scripts/crypto_valuation.py uniswap --revenue 85000000 --base-growth 0.55
```

### [review-revenue-estimator](review-revenue-estimator/)
Estimates monthly and annual revenue ranges for local businesses from Google, Yelp, and Meta review velocity, ticket size, and industry priors. Not for public-company earnings or pure e-commerce.

```bash
python review-revenue-estimator/scripts/estimate_revenue.py \
  --name "Example Auto Repair" --location "Portland, PA" \
  --industry auto_services --location-tier rural \
  --google-reviews 151 --google-rating 4.8 --google-velocity 6 --bays 3
```

## Layout

```
crypto-project-analysis/
crypto-valuation-analyst/
review-revenue-estimator/
```

Copy a skill folder into your agent's skills directory, or clone this repo and point the agent at it.

## Disclaimer

Not financial, investment, or business-valuation advice. Verify on-chain data, audits, unlock schedules, and business figures independently.
