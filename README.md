# CryptoMetrics-Powerbi

A simple, self-hosted dashboard tracking cryptocurrency metrics using **CoinGecko API** → **SQLite** → **Power BI**.

## Features
- Daily snapshots of top ~250 coins by market cap (price, volume, market cap, 24h/7d/30d changes, ATH, etc.).
- Global market metrics (total market cap, 24h volume, BTC dominance).
- Time-series data for historical analysis (daily snapshots enable charts over time).
- Easy refresh in Power BI.

## Setup
1. `git clone` this repo (or download).
2. `pip install -r requirements.txt`
3. Run data ingestion: `python etl/fetch_crypto_data.py` (run daily via cron/task scheduler).
4. Install **SQLite ODBC Driver** (required for Power BI):
   - Download: http://www.ch-werner.de/sqliteodbc/ (32-bit or 64-bit matching your Power BI).
   - Install and confirm "SQLite3 ODBC Driver" appears in ODBC Administrator.
5. Open **Power BI Desktop** → Get Data → ODBC → Advanced Options:
   - Connection string: `DRIVER={SQLite3 ODBC Driver};Database=full\path\to\data\crypto.db`
   - Load tables: `snapshots` and `global_metrics`.
6. Build visuals (see powerbi_setup.md for details).

## Metrics Tracked
- Top coins by market cap, price changes, volume.
- Global totals and BTC dominance.
- Historical price/market cap trends via date snapshots.

## Notes
- CoinGecko free API (no key needed, respect rate limits ~30 calls/min).
- SQLite file is local; for production, consider PostgreSQL or scheduled cloud runs.
- Add your own .pbix file to the repo if desired (gitignore large binaries if preferred).



# Crypto Metrics Power BI / SQL Dashboard / Yield farming/ NFTs


## New Features (Yield Farming & NFT Trackers)
- **Yield Farming Dashboard**: Top pools by APY (base/reward), TVL, chains/projects like Aave, Uniswap. Sort for best opportunities.
- **NFT Collections Dashboard**: Top 100 collections by 24h volume (Ethereum focus), with floor price, sales count, avg price.
- Data from DeFi Llama (yields) & OpenSea (NFTs—needs free API key).

## Setup Additions
- Get OpenSea API key: Sign up at opensea.io, go to API section, generate key.
- Add to env or hardcode in script (for testing): `OPENSEA_API_KEY = 'your_key'`
- Run `python etl/fetch_crypto_data.py` — now fetches all data.
- In Power BI, load new tables: `yield_pools` and `nft_collections`.
- Build new pages/visuals (see powerbi_setup.md).

Notes: OpenSea rate limits ~4 req/sec; respect it. For more chains/NFTs, tweak params.
