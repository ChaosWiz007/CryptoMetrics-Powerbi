## Power BI Dashboard Setup

After loading tables:

### Recommended Visuals
- **Cards**: Total Market Cap, BTC Dominance (use LASTDATE or MAX(date) filter), 24h Volume.
- **Bar/Column Chart**: Top 10 coins by market_cap (use RANKX in DAX or Top N filter).
- **Line Chart**: Price over time (date on axis, current_price on values, coin slicer or filter for 'bitcoin').
- **Table/Matrix**: Top coins with price changes, volume, % changes.
- **Slicer**: Coin selection, Date range.

### Example DAX Measures
Total Market Cap = 
CALCULATE(
    SUM(global_metrics[total_market_cap_usd]),
    LASTDATE(global_metrics[date])
)

BTC Dominance % = 
CALCULATE(
    AVERAGE(global_metrics[btc_dominance]),
    LASTDATE(global_metrics[date])
)

Daily Price Change % (selected coin) = 
AVERAGE(snapshots[price_change_pct_24h])

# For volatility (example)
30d Volatility = STDEV.P(snapshots[price_change_pct_30d])  // or custom rolling

# Top N helper if needed
Market Cap Rank = RANKX(ALL(snapshots), snapshots[market_cap], , DESC, Dense)
