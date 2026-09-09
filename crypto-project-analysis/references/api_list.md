# Free Keyless Crypto APIs Used in This Skill

This skill leverages the following free (or free-tier) keyless APIs from your provided list. Scripts implement fallbacks and respect rate limits.

## Market & Price Data
- CoinGecko — Primary source for price, market cap, FDV, volume, supply (most comprehensive)
- Coinpaprika — Strong fallback with good tokenomics fields
- CoinStats, Coinlore, CryptoCompare, CoinCap, Cryptonator, Gemini, Exchangerate.host, CoinDesk BPI, Walltime, Bitcambio, Nexchange, Localbitcoins, CryptingUp, CryptAPI
- Messari — Asset endpoints and research-grade data

## On-Chain / Bitcoin
- btcnode.uk — Bitcoin blockchain data, fees, mempool, SEC insider trades, Reddit sentiment (some endpoints free or x402 micropay)
- Mempool — Bitcoin API Service (fees, mempool, blocks)
- BitcoinCharts — Financial and technical Bitcoin data

## DEX & Liquidity
- 0x API — Token and pool stats across liquidity pools
- 1inch API — Decentralized exchange queries and quotes

## Solana & Other Chains
- Solana JSON RPC — Public endpoints for token supply, account info, program state
- ZMOK — Ethereum JSON RPC / Web3 provider (alternative if needed)

## Specialized / Niche
- Chainlink Build — Hybrid smart contracts reference
- Helium, Steem — Network data (contextual)
- Block Lottos — On-chain lottery endpoints
- Alpha (Mossland) — Korean crypto channel stance + RAG Q&A + entity store (useful for narrative sentiment in certain markets)
- TWZRD Agent Intel — Solana on-chain agent trust scoring (MCP tools for AI agent wallets)

## Notes on Usage in Checklist
- **Tokenomics / Capital Structure signals** (Section 3.3): Use market_data.py for FDV/MC ratio, circulating vs total supply. Full vesting/unlock schedules and private investor allocation % usually require project whitepaper + Tokenomist-style sources (not fully automated here).
- **Quantitative metrics** (Section 4): market_data + onchain_bitcoin + dex_stats + solana_rpc cover price action, liquidity depth, fee pressure, supply dynamics.
- **Risk flags**: Low liquidity (dex_stats), high FDV/MC (market_data), mempool/fee spikes (onchain_bitcoin) feed directly into red flag assessment.
- Always cross-verify critical numbers across 2+ sources. These are public endpoints — they can change or rate-limit.

For full due diligence, combine script output with manual qualitative work (team, audits, narrative, competitive SWOT with mitigants) as outlined in references/Crypto_Project_Analysis_Checklist.pdf.
