import requests
import sqlite3
from datetime import date
from pathlib import Path
import os  # for API key

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "crypto.db"

OPENSEA_API_KEY = os.environ.get('OPENSEA_API_KEY', 'your_opensea_api_key_here')  # Replace or use env var

def create_tables(conn):
    cursor = conn.cursor()
    # Existing tables (keep)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            date TEXT,
            coin_id TEXT,
            symbol TEXT,
            name TEXT,
            current_price REAL,
            market_cap REAL,
            total_volume REAL,
            price_change_24h REAL,
            price_change_pct_24h REAL,
            price_change_pct_7d REAL,
            price_change_pct_30d REAL,
            ath REAL,
            ath_date TEXT,
            last_updated TEXT,
            PRIMARY KEY (date, coin_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_metrics (
            date TEXT PRIMARY KEY,
            total_market_cap_usd REAL,
            total_volume_usd REAL,
            btc_dominance REAL
        )
    ''')
    # New: Yield Pools
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS yield_pools (
            date TEXT,
            pool_id TEXT,
            chain TEXT,
            project TEXT,
            symbol TEXT,
            tvl_usd REAL,
            apy REAL,
            apy_base REAL,
            apy_reward REAL,
            volume_usd_1d REAL,
            stablecoin INTEGER,
            PRIMARY KEY (date, pool_id)
        )
    ''')
    # New: NFT Collections
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nft_collections (
            date TEXT,
            slug TEXT,
            name TEXT,
            floor_price_eth REAL,
            floor_price_usd REAL,
            one_day_volume_eth REAL,
            one_day_volume_usd REAL,
            one_day_sales REAL,
            one_day_avg_price_eth REAL,
            total_supply INTEGER,
            num_owners INTEGER,
            PRIMARY KEY (date, slug)
        )
    ''')
    conn.commit()

def fetch_yields(conn):
    today = date.today().isoformat()
    url = "https://yields.llama.fi/pools"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()['data']
    # Sort by APY desc, take top 250 for best opportunities
    top_yields = sorted(data, key=lambda x: x.get('apy', 0), reverse=True)[:250]
    
    cursor = conn.cursor()
    for pool in top_yields:
        cursor.execute('''
            INSERT OR REPLACE INTO yield_pools 
            (date, pool_id, chain, project, symbol, tvl_usd, apy, apy_base, apy_reward, volume_usd_1d, stablecoin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            today, pool.get('pool'), pool.get('chain'), pool.get('project'), pool.get('symbol'),
            pool.get('tvlUsd'), pool.get('apy'), pool.get('apyBase'), pool.get('apyReward'),
            pool.get('volumeUsd1d'), 1 if pool.get('stablecoin') else 0
        ))
    conn.commit()
    print(f"Fetched {len(top_yields)} top yield pools for {today}.")

def fetch_nfts(conn):
    today = date.today().isoformat()
    url = "https://api.opensea.io/v2/collections"
    params = {
        "chain_identifier": "ethereum",  # Focus on ETH for top volume; add others if needed
        "order_by": "one_day_volume",
        "order_direction": "desc",
        "limit": 100  # Top 100 by volume
    }
    headers = {"X-API-KEY": OPENSEA_API_KEY}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    collections = resp.json()['collections']
    
    cursor = conn.cursor()
    for coll in collections:
        stats = coll.get('stats', {}) or {}
        cursor.execute('''
            INSERT OR REPLACE INTO nft_collections 
            (date, slug, name, floor_price_eth, floor_price_usd, one_day_volume_eth, 
             one_day_volume_usd, one_day_sales, one_day_avg_price_eth, total_supply, num_owners)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            today, coll.get('slug'), coll.get('name'),
            stats.get('floor_price'), stats.get('floor_price_usd'),
            stats.get('one_day_volume'), stats.get('one_day_volume_usd'),
            stats.get('one_day_sales'), stats.get('one_day_average_price'),
            coll.get('total_supply'), coll.get('num_owners')
        ))
    conn.commit()
    print(f"Fetched {len(collections)} top NFT collections for {today}.")

def fetch_and_store():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    
    # Existing fetches (coins & global)
    today = date.today().isoformat()
    cursor = conn.cursor()

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "price_change_percentage": "24h,7d,30d",
        "sparkline": "false"
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    markets = resp.json()

    for coin in markets:
        cursor.execute('''
            INSERT OR REPLACE INTO snapshots 
            (date, coin_id, symbol, name, current_price, market_cap, total_volume, 
             price_change_24h, price_change_pct_24h, price_change_pct_7d, price_change_pct_30d,
             ath, ath_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            today, coin.get('id'), coin.get('symbol'), coin.get('name'),
            coin.get('current_price'), coin.get('market_cap'), coin.get('total_volume'),
            coin.get('price_change_24h'), coin.get('price_change_percentage_24h'),
            coin.get('price_change_percentage_7d_in_currency'),
            coin.get('price_change_percentage_30d_in_currency'),
            coin.get('ath'), coin.get('ath_date'), coin.get('last_updated')
        ))

    resp = requests.get("https://api.coingecko.com/api/v3/global", timeout=15)
    resp.raise_for_status()
    gdata = resp.json()['data']
    cursor.execute('''
        INSERT OR REPLACE INTO global_metrics 
        (date, total_market_cap_usd, total_volume_usd, btc_dominance)
        VALUES (?, ?, ?, ?)
    ''', (
        today,
        gdata['total_market_cap'].get('usd'),
        gdata['total_volume'].get('usd'),
        gdata.get('btc_dominance')
    ))

    # New fetches
    fetch_yields(conn)
    fetch_nfts(conn)
    
    conn.commit()
    conn.close()
    print(f"All data updated for {today}.")

if __name__ == "__main__":
    fetch_and_store()
