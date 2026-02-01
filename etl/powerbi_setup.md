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




# New Section Added

### New: Yield Farming Dashboard (New Page)
Visualize best opportunities—create a new page in your .pbix.

- **Slicers**: Chain (e.g., Ethereum, Arbitrum), Project (e.g., Uniswap), Stablecoin (Yes/No).
- **Table**: Top pools by APY—columns: Symbol, Chain, Project, APY (%), Base APY, Reward APY, TVL ($).
- **Bar Chart**: Top 10 by TVL or APY.
- **Cards**: Avg APY (top 50), Total TVL in top pools.
- **Line Chart**: APY trends over time (if running daily for history).

Example DAX:
Top APY = TOPN(10, yield_pools, yield_pools[apy], DESC)
Avg APY = AVERAGE(yield_pools[apy])
High Yield Count = COUNTROWS(FILTER(yield_pools, yield_pools[apy] > 10))

Here's a vibe for what it could look like (inspired by pro setups):

<grok-card data-id="586cfa" data-type="image_card" data-plain-type="render_searched_image"  data-arg-size="LARGE" ></grok-card>


### New: NFT Collections Dashboard (New Page)
Track hot collections by volume.

- **Slicers**: Name or Slug filter.
- **Table**: Top by 1d Volume—columns: Name, Floor Price (ETH/USD), 1d Volume (ETH/USD), Sales Count, Avg Price.
- **Column Chart**: Volume breakdown top 20.
- **Cards**: Total 1d Volume, Avg Floor Price, Hottest Collection (MAX volume).
- **Scatter Plot**: Volume vs Floor Price (bubble size = Sales).

Example DAX:
Top Volume Rank = RANKX(ALL(nft_collections), nft_collections[one_day_volume_usd], , DESC)
Total NFT Volume = SUM(nft_collections[one_day_volume_usd])

Visual inspo for your NFT tracker:

<grok-card data-id="1a6460" data-type="image_card" data-plain-type="render_searched_image"  data-arg-size="LARGE" ></grok-card>


## Enhancements
- For historical trends: Run script daily to build time-series (e.g., APY changes, volume spikes).
- Alerts: In Power BI, set data alerts for APY > 50% or volume surges.
- Expand: Add more chains to OpenSea params (e.g., polygon) or fetch specific collection history.
