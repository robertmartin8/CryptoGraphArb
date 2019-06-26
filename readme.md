# CryptoGraphArb

This is the supporting code for my [post](https://reasonabledeviations.science/2019/04/21/currency-arbitrage-graphs-2/) on using graph theory to discover arbitrage opportunities in a cryptocurrency market.

To run it, first sign up to [CryptoCompare](https://min-api.cryptocompare.com/) to get a free API key. Replace it after the equals sign at the top of `cryptocompare_scraper.py`.

- `cryptocompare_scraper.py` downloads the raw data, creating `pairs_list.json`, `binance_data/` and `snapshot.csv`.
- `graph_arbitrage.py` processes this data and puts it into a graph, before running Bellman-Ford to find arbitrage opportunities.
