import requests
import sqlite3
from datetime import date
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "crypto.db"

def create_tables(conn):
    cursor = conn.cursor()
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
    conn.commit()

def fetch_and_store():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    cursor = conn.cursor()
    today = date.today().isoformat()

    # Fetch coin markets
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

    # Fetch global
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

    conn.commit()
    conn.close()
    print(f"Data updated for {today} - {len(markets)} coins.")

if __name__ == "__main__":
    fetch_and_store()
