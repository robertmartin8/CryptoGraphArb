# CryptoGraphArb

<center>
<img src="https://reasonabledeviations.com/assets/images/weighted_digraph.png" style="width:50%;"/>
</center>

This is the supporting code for my [post](https://reasonabledeviations.com/2019/04/21/currency-arbitrage-graphs-2/) on using graph theory to discover arbitrage opportunities in a cryptocurrency market.

## Getting started

To run it, first sign up to [CryptoCompare](https://min-api.cryptocompare.com/) to get a free API key. Then, you can either replace it after the equals sign at the top of `cryptocompare_scraper.py`, or create a new text file named `API_KEY.txt` and paste it there directly.

Then, install dependencies with:

```bash
pip install -r requirements.txt
```

Lastly, run the code:

```bash
python cryptocompare_scraper.py
python graph_arbitrage.py
```

## Overview

- `cryptocompare_scraper.py` downloads the raw data, creating `pairs_list.json`, `binance_data/` and `snapshot.csv`.
- `graph_arbitrage.py` processes this data and puts it into a graph, before running Bellman-Ford to find arbitrage opportunities.

## Your turn

Here's a brief list of a few ways that you could extend this project. Some are trivial, some are not!

- Model transaction fees. This is literally one line of code, multiplying the arbitrage value by e.g 0.999 for each element in the path.
- Download data from more exchanges. `graph_arbitrage.py` operates completely independently of the data collection, it just needs an adjacency matrix.
- Automatically run the code at fixed intervals to continuously look for arbitrage.
- Modify the Bellman-Ford so that it doesn't have to recompute everything when some weights change.
