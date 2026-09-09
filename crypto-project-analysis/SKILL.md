---
name: crypto-project-analysis
description: Autonomous due diligence ONLY for native crypto tokens, protocols, DeFi projects, L1/L2 chains and on-chain assets following the Crypto Project Analysis Checklist. Explicitly excludes ETFs, public equities (e.g. COIN, MSTR), crypto mining companies, and traditional holding companies. If user does not supply thesis, goal, narrative, or other inputs, the agent proactively derives them from market sentiment ("Where is the market at?"), quantitative signals from the free keyless API basket (CoinGecko, Coinpaprika, 0x, 1inch, Solana RPC, btcnode.uk, Mempool, GitHub public API), and web/X searches as fallback. Prioritizes existing scripts/APIs, falls back to general search. Provides quantitative proxies for team track record, community metrics, tokenomics signals, product/security. Scoring is data-driven and non-arbitrary. The agent MUST always show its full work and reasoning. Use for end-to-end analysis with minimal user input (just project identifier).
---

# Crypto Project Analysis Skill (Autonomous + Free Keyless APIs)

## Purpose
This skill makes the Crypto Project Analysis Checklist fully actionable with minimal user input **for native crypto tokens and on-chain projects only**. It automates data fetching via scripts for the API basket and provides clear instructions for the agent to autonomously fill gaps using quantitative methods and searches when user does not supply thesis, core goal, narrative narrowing, team details, community metrics, vesting schedules, etc. 

**Transparency Requirement**: The agent must always show its full reasoning, data sources, score justifications, and why a particular recommendation was made. Black-box recommendations are not allowed.

**Core Philosophy**: "Where is the market at?" is the default starting question. The agent derives thesis, goal, risk/reward, and narrows themes based on current market sentiment + project data, always "taking what the market gives us". Qualitative elements are supported by quantitative proxies wherever possible. The agent scores in a structured, non-arbitrary way and explicitly flags unmitigated issues in SWOT without forcing mitigants.

## Scope: What This Skill Analyzes (Strict Limits)
This skill is **exclusively** for **native crypto tokens, protocols, DeFi applications, L1/L2 blockchains, and on-chain projects**.

**It must NOT analyze or recommend:**
- Publicly traded equities or stocks (e.g. COIN/Coinbase, MSTR/MicroStrategy, MARA, RIOT, or any crypto mining/holding company)
- ETFs or ETPs (e.g. IBIT, GBTC, or any Bitcoin/Ethereum ETF)
- Traditional finance companies that merely hold crypto

**Early Scope Check (Mandatory)**: 
At the very beginning of any analysis, confirm the target is a native on-chain crypto project/token. 
- If the query is about a public equity, ETF, or miner → Politely decline and explain: "This skill only analyzes native crypto tokens and on-chain projects (e.g. PEPE, Uniswap, Solana ecosystem protocols). For public equities like COIN or MSTR, please use general market analysis tools instead."
- Only proceed with on-chain crypto assets.

This prevents drift into traditional equities.

## When to Activate
- User provides a **native crypto token or on-chain project** identifier (symbol like "PEPE", "UNI", name like "Uniswap", or contract/mint address) and wants full due diligence.
- Running the full checklist end-to-end with autonomous gap-filling for on-chain crypto assets only.
- Needing market regime assessment, sentiment-driven thesis, quantitative team/community/tokenomics proxies, or data-driven scoring **for crypto projects/tokens**.
- Building/updating the scorecard when inputs are sparse.

**Do not activate** for public equities (COIN, MSTR, miners), ETFs, or traditional companies. Redirect those queries.

## Autonomous Mode — Default Behavior When Inputs Are Missing
If the user does **not** provide a thesis, core goal, success metrics, narrative/theme, or specific analysis angles, the agent **must** operate autonomously as follows:

**Mandatory First Step — Scope Confirmation**:
Before doing any analysis, confirm this is a **native crypto token or on-chain project** (not a public stock, ETF, or mining company). If it is not, immediately respond with the scope limitation explained above and do not proceed.

1. **Start with "Where is the market at?"**
   - Use tools to assess current crypto market regime and sentiment:
     - Run market_data.py and onchain_bitcoin.py for macro signals (prices, volume, fees, mempool size as congestion/stress indicators).
     - Use web_search or x_keyword_search / x_semantic_search for "current crypto market sentiment [today's date or recent]" or "hot crypto narratives right now".
     - Identify dominant regime (accumulation, markup, distribution, markdown) and hot/cold narratives.
   - This informs everything downstream.

2. **Derive Thesis & Core Goal (if not supplied)**
   - Base on market sentiment + project fit.
   - Example: If market shows strength in a narrative the project participates in (e.g., strong on-chain metrics + positive sentiment in "AI agents"), derive thesis around asymmetric upside in that narrative.
   - Core goal depends on sentiment: 
     - Bullish momentum → Speculative asymmetric upside trade.
     - Accumulation/contrarian setup → Long-term conviction hold or yield/governance play.
     - Weak market but strong project fundamentals → High-conviction contrarian position.
   - Always tie to "take what the market gives us" — do not fight the tape.

3. **Narrow Theme (if not supplied)**
   - Use sentiment data + existing narrowing instructions from the checklist.
   - Example: Broad "AI crypto" is too wide. If sentiment shows momentum specifically in "verifiable compute / decentralized agents on Solana" with near-term catalysts (upcoming mainnet, partnerships, on-chain activity spike), narrow to that specific, actionable narrative.
   - Avoid broad narratives unless sentiment strongly supports them.

4. **Fill Quantitative & Proxy Sections Autonomously** (align to updated checklist sections 1-5):
   - **Transaction Summary & Theme (Sections 1-2)**: Derive Core Goal, Time Horizon, Success/Failure Metrics, Narrative Cycle position, Macro Fit from market sentiment + project data.
   - **Market / Token Data, Comps, Macro Cycle, Filter Test (Sections 2, 4.1)**: 
     - Primary: Run `market_data.py`, `onchain_bitcoin.py`, `dex_stats.py`, `solana_rpc.py`.
     - Comps: Pull data for 3-5 peer projects via market_data.py and compare FDV/MC, volume, supply dynamics, performance.
     - Macro/Filter: Use FDV/MC ratios (categorize dilution risk per checklist), liquidity depth, fee/mempool signals, holder trends quantitatively.
     - If API data insufficient → web_search or browse_page the project docs/explorer pages.
   - **Team, Founders & Execution (3.1)**: Quantitative proxy via search.
     - Search: "[founder names or team] crypto background years experience previous projects performance exits".
     - Measure: Approximate years in crypto/web3, number of notable past projects, performance signals (successful exits, ROI mentions, failures with lessons).
     - If no clear public team → flag as higher risk (anon team penalty in scoring).
   - **Community, Distribution & Governance (3.2)**: Quantitative where possible.
     - GitHub activity: Run `github_activity.py owner/repo` (stars, forks, recent activity as proxy for developer health and organic interest).
     - Mentions/distribution + sentiment: Use x_keyword_search or x_semantic_search for recent project mentions; analyze volume + sentiment (organic discussion vs bot/paid).
     - Active governance: Search for recent proposals, voting turnout, quality.
     - Wallet concentration: Search or browse on-chain explorers (Arkham, Solscan, etc.) for top holder %.
     - If scripts/APIs limited → web_search " [project] holder concentration" or " [project] governance activity".
   - **Tokenomics & Capital Structure signals (4.2)**: Heavily quantitative.
     - Allocation, float at TGE, supply dynamics: Primary from `market_data.py` (FDV/MC, circulating/total/max supply). Higher float at launch = positive signal (per research in attachments).
     - Vesting/unlock schedule, acceleration clauses: Search project whitepaper/tokenomics docs or summaries (" [project] token vesting schedule Tokenomist" or official docs). On-chain where visible (e.g., via Solana RPC or unlock contracts).
     - Real utility & value accrual: Search " [project] token utility value accrual fees to stakers burns buybacks" or protocol revenue data. Distinguish sustainable (real fees captured by token) vs inflationary (emissions only).
     - Dilution stress test: Model using supply data + known unlocks (from search); flag high future dilution risk if FDV/MC high + large unlocks soon.
     - If on-chain implementation available (e.g., via explorers) → use it; otherwise docs/search. Reference the capital structure table in `references/Crypto_Project_Transaction_Memo_Checklist.md` (§4.2).
   - **Product, Tech, and Security (3.3)**: 
     - GitHub: Run `github_activity.py` for code activity level.
     - Audits, code quality, upgradability, dependencies, regulatory: Search " [project] smart contract audit report", " [project] github", project docs, or known security incidents.
     - Prioritize reputable sources; flag missing audits or critical unresolved issues. Include dependencies, bridge risks, etc.
   - **Competitive Landscape, Moat & SWOT with Mitigants (3.4)**: Agent completes qualitatively but informed by quantitative data.
     - Use data from above (metrics vs peers for moat strength, on-chain usage for differentiation).
     - **Critical rule**: Do not stretch to invent mitigants. If a weakness/threat has no credible positive offset based on data, explicitly flag it as "unmitigated risk" and note impact on thesis.
     - SWOT should be evidence-based; avoid narrative stretching. Use Porter's Five Forces where relevant.
   - **Market / Token Data, Comps, Macro Cycle, Filter Test (Sections 2, 4.1)**: 
     - Primary: Run `market_data.py`, `onchain_bitcoin.py`, `dex_stats.py`, `solana_rpc.py`.
     - Comps: Pull data for 3-5 peer projects via market_data.py and compare FDV/MC, volume, supply dynamics, performance.
     - Macro/Filter: Use FDV/MC ratios, liquidity depth, fee/mempool signals, holder trends quantitatively.
     - If API data insufficient for specific comp or macro detail → web_search or browse_page the project docs/explorer pages.
   - **Team, Founders & Execution (3.1)**: Quantitative proxy via search.
     - Search: "[founder names or team] crypto background years experience previous projects performance exits".
     - Measure: Approximate years in crypto/web3, number of notable past projects, performance signals (successful exits, ROI mentions, failures with lessons).
     - If no clear public team → flag as higher risk (anon team penalty in scoring).
   - **Community, Distribution & Governance (3.2)**: Quantitative where possible.
     - GitHub activity: Run `github_activity.py owner/repo` (stars, forks, recent activity as proxy for developer health and organic interest).
     - Mentions/distribution + sentiment: Use x_keyword_search or x_semantic_search for recent project mentions; analyze volume + sentiment (organic discussion vs bot/paid).
     - Active governance: Search for recent proposals, voting turnout, quality.
     - Wallet concentration: Search or browse on-chain explorers (Arkham, Solscan, etc.) for top holder %.
     - If scripts/APIs limited → web_search " [project] holder concentration" or " [project] governance activity".
   - **Tokenomics & Capital Structure signals (4.2)**: Heavily quantitative.
     - Allocation, float at TGE, supply dynamics: Primary from `market_data.py` (FDV/MC, circulating/total/max supply). Higher float at launch = positive signal (per research).
     - Vesting/unlock schedule, acceleration clauses: Search project whitepaper/tokenomics docs or summaries (" [project] token vesting schedule Tokenomist" or official docs). On-chain where visible (e.g., via Solana RPC or unlock contracts).
     - Real utility & value accrual: Search " [project] token utility value accrual fees to stakers burns buybacks" or protocol revenue data. Distinguish sustainable (real fees captured by token) vs inflationary (emissions only).
     - Dilution stress test: Model using supply data + known unlocks (from search); flag high future dilution risk if FDV/MC high + large unlocks soon.
     - If on-chain implementation available (e.g., via explorers) → use it; otherwise docs/search.
   - **Product, Tech, and Security (3.3)**: 
     - GitHub: Run `github_activity.py` for code activity level.
     - Audits, code quality, upgradability, dependencies, regulatory: Search " [project] smart contract audit report", " [project] github", project docs, or known security incidents.
     - Prioritize reputable sources; flag missing audits or critical unresolved issues.
   - **Competitive Landscape, Moat & SWOT with Mitigants (3.4)**: Agent completes qualitatively but informed by quantitative data.
     - Use data from above (metrics vs peers for moat strength, on-chain usage for differentiation).
     - **Critical rule**: Do not stretch to invent mitigants. If a weakness/threat has no credible positive offset based on data, explicitly flag it as "unmitigated risk" and note impact on thesis.
     - SWOT should be evidence-based; avoid narrative stretching.

5. **Rough Risk/Reward & Edge + Full 4.3 Valuation (Sections 1, 4.3, 5)**: 
   - **Mandatory**: Run `python scripts/crypto_valuation.py <id>` (it auto-applies market defaults + any regime signals from price action). Incorporate ALL outputs: scenarios, stress test dilution, price floor, comps, and aggregate high/low/avg/median review.
   - Edge exists where project shows strong quantitative signals (good float at TGE per empirical research, real sustainable value accrual, active dev, organic community) + favorable narrative cycle fit, in a market regime that undervalues it.
   - Risk/reward calibrated to sentiment. Explicitly call out red flags from 5.1 (high team+investor alloc + short vesting, anon team + whale conc, low TGE float, security incidents/poor audits, treasury opacity, narrative overextension, manipulation risks from low liq/high conc, legal issues). Classify each as unrelated / mitigated / unmitigated.
   - Use the valuation review (median/expected) + red flag count to calibrate conviction and position size.
   - Edge exists where project shows strong quantitative signals (good float, real value accrual, active development, organic community) in a market regime that undervalues it or where sentiment is shifting positively toward its narrative.
   - Risk/reward calibrated to sentiment (higher upside in recovering market, more conservative sizing in euphoric or uncertain regimes).

6. **Scoring — Quantitative & Non-Arbitrary**
   - Use a structured rubric (example below; agent should adapt slightly based on data availability but stay consistent and justify every point).
   - Assign points per category based on measurable signals. Weighted total out of ~100. Clear thresholds:
     - 80+ : Strong Conviction Buy / Accumulate
     - 60-79 : Buy on dips / Watch with position
     - 40-59 : Hold / Selective or small speculative
     - <40 : Pass or high-risk only with tiny size
   - Example Rubric (adjust weights per thesis priority; document changes):
     - **Thesis Fit & Market Regime (15 pts)**: Strong alignment with current sentiment/hot narrative + quantitative macro support = high score.
     - **Tokenomics, Capital Structure & Dilution Stress (20 pts)**: High initial float at TGE / low future dilution risk per stress test (+), real sustainable value accrual / revenue to token (+), reasonable vesting/unlock schedule aligned with successful comps (+). Deduct for high team+investor alloc + short vesting or unmitigated dilution overhang from valuation script output.
     - **Team & Execution Proxy (10 pts)**: Public team with track record (years exp + successful past projects) = positive; anon or weak history = penalty.
     - **Community & Governance (15 pts)**: High GitHub activity + organic mentions/sentiment + active governance + reasonable holder concentration = high.
     - **Product/Tech/Security (15 pts)**: Active GitHub + multiple reputable audits + no major unresolved issues + real utility = high.
     - **Competitive Moat & Quantitative Edge (15 pts)**: Clear differentiation backed by metrics (usage growth, liquidity depth, retention) vs peers; unmitigated weaknesses flagged and deducted.
     - **Risk Flags, Valuation Coherence & Overall (10 pts)**: Few/no major red flags from 5.1 + valuation outputs coherent with thesis (e.g. median estimate supports upside, stress test manageable) = high. Multiple unmitigated risks or valuation showing extreme downside/dilution = deduction. Cross-reference aggregate review (high/low spread) for uncertainty flag.
   - Every score must cite specific data source (e.g., "CoinGecko FDV/MC 1.4 → +3 pts"; "GitHub stars 45k + recent commits → +2 pts"; "Search: no public team track record found → -4 pts").

7. **Synthesis, Recommendation & Full Transparency (Mandatory)**
   - Combine all autonomous data + any user-provided inputs.
   - Update the one-page scorecard with scores + justifications.
   - Define entry/exit based on derived thesis invalidation points and quantitative signals.
   - **Show Your Full Work**: The final output to the user **must** include:
     - The complete step-by-step reasoning (how "Where is the market at?" led to the thesis and goal).
     - All data sources used (which scripts were run, which searches performed, key numbers pulled).
     - Point-by-point justification for every score in the rubric.
     - How sentiment influenced narrowing, risk/reward, and edge.
     - Any unmitigated risks explicitly called out.
     - A clear narrative explaining *why* the final recommendation was made (not just the score).
   - Never give a recommendation without showing the underlying due diligence and reasoning. The user must be able to understand and verify every conclusion.

## Core Instructions — Follow the Playbook (Autonomously Where Needed)
Always start with the full **Crypto Project Transaction Memo Checklist** in `references/Crypto_Project_Transaction_Memo_Checklist.md` (lossless markdown of the publish-ready final draft). This is the Banker's Due Diligence Framework adapted for tokens/protocols (Sections 1-5 exactly as published). It covers:
1. Transaction Proposal Summary (thesis, goal, metrics, sizing, edge)
2. Proposal Theme (narrative narrowing, cycle position, macro fit)
3. Project Background (Team/Founders/Execution, Community/Distribution/Governance, Product/Tech/Security with dependencies & regulatory, Competitive Landscape/Moat/SWOT-with-mitigants rule, Porter's 5 Forces)
4. On-Chain Analysis (4.1 Market/Fundamental Metrics, 4.2 Tokenomics & Capital Structure as cap table analog, **4.3 Forecasting/Valuation/Benchmarking/Stress Testing**)
5. Conclusion (5.1 Red Flags and Risk Mitigation, 5.2 Scoring and Decision with hurdle rate, inflection points, position sizing, monitoring)

**Critical Rule from Checklist**: Every negative (weakness/threat) must be offset by a **credible positive mitigant**. If none exists, explicitly flag as "unmitigated risk" — do not stretch.

**If user supplies thesis/goal/narrative/details**: Use them + enhance with data/scripts.

**If not supplied (default autonomous path)**: Follow the Autonomous Mode section above to derive and populate.

**Step-by-step data pull (prioritize APIs/scripts first)**:
- Market/Token/Comps/Dilution proxy: `python scripts/market_data.py <id>`
- On-chain BTC/macro: `python scripts/onchain_bitcoin.py fees|mempool|stats`
- DEX liquidity: `python scripts/dex_stats.py <address> [chain]`
- Solana-specific: `python scripts/solana_rpc.py <mint> getTokenSupply|getAccountInfo`
- GitHub activity (new): `python scripts/github_activity.py owner/repo`
- **Valuation (4.3 Forecasting, Valuation, Benchmarking, Stress Testing)**: `python scripts/crypto_valuation.py <id> [--revenue XXX --base-growth 0.XX etc.]` — This new script bakes in market-calibrated defaults (growth rates, discount 42%, dilution assumptions, regime adjustments from 30d price action) when no custom thesis/inputs provided. Always run it for the valuation section and incorporate outputs (scenarios, stress test, floor, comps, aggregate review) into your synthesis.
- For gaps (team track record, vesting details, audits, sentiment nuance, specific comps, governance): Use web_search, browse_page on project docs/explorers, or x_keyword_search / x_semantic_search for recent sentiment/mentions.
- Cross-verify critical numbers across 2+ sources.

**Step 6: Synthesize & Score**
- Use the quantitative rubric above.
- Update scorecard in the checklist document.
- Re-run key scripts before major decisions or on events (unlocks, news, sentiment shifts).
- Document fully: "Autonomous run on [date]. Sources: CoinGecko + GitHub API + web_search for team/vesting + X sentiment search."

## API Coverage & Notes (Prioritize These)
- **Primary Scripts (always try first)**: market_data.py (CoinGecko primary + fallbacks), onchain_bitcoin.py, dex_stats.py, solana_rpc.py, github_activity.py (new), **crypto_valuation.py** (for autonomous 4.3 valuation with baked-in market assumptions).
- **Sentiment & Narrative Narrowing**: X tools (x_keyword_search, x_semantic_search) or web_search for market/project sentiment.
- **Team/Track Record, Vesting, Audits, Specific Docs**: web_search + browse_page on official sources, whitepapers, Tokenomist-like summaries, explorer pages.
- **On-chain deeper** (holder concentration, some unlocks): Browse Arkham, Solscan, Dune (free tiers) or search summaries.
- Many traditional "qualitative" items now have strong quantitative proxies or search fallbacks. The agent should default to data over speculation.

## Error Handling, Sandbox & Best Practices
- Scripts fail gracefully (connection issues in sandbox show clear warnings + error JSON with suggestions). In sandbox: Use the Sandbox section guidance (search specific sites like coingecko.com, mempool.space, github.com, project docs).
- Always prioritize existing API basket/scripts → general web/X search.
- Verify critical data (supply, vesting, audits) from multiple sources.
- For competitive/SWOT: Be rigorous — flag unmitigated risks explicitly rather than stretching for mitigants.
- Respect rate limits on all public APIs and search tools.
- This skill + checklist enables near end-to-end autonomous analysis. User can override any derived element.

## Export / Standalone Use
The skill directory is self-contained. Scripts use stdlib + public APIs (keyless where possible). For full autonomous runs outside sandbox, ensure internet access. 

**New in this pack**: `crypto_valuation.py` implements full §4.3 (all methods + baked-in market assumptions + aggregate review). It is used by this skill and powers the companion **Crypto Valuation Analyst** skill (focused, valuation-only reports).

**To use the valuation module standalone or in other agents (Grok, Claude, local)**:
- CLI: `python scripts/crypto_valuation.py bitcoin --revenue 120000000 --base-growth 0.6`
- Library: Import `generate_valuation_report(project_id, custom_assumptions_dict)` → returns (markdown_report, structured_json_dict)
- See the exportable pack in /artifacts/crypto-analysis-pack/ for full setup across environments.

Run validation after edits:
bash /root/.grok/skills/skill-creator/scripts/validate-skill.sh /home/workdir/.grok/skills/crypto-project-analysis
