import pandas as pd
import requests
import os
import json
from tqdm import tqdm

AUTH = ""


def top_exchange_pairs():
    """
    Returns all pairs from the top exchances (according to CryptoCompare),
    then writes the result to pairs_list.json.
    """
    url = (
        "https://min-api.cryptocompare.com/data/v3/all/exchanges?topTier=true&api_key="
        + AUTH
    )
    r = requests.get(url)
    with open("pairs_list.json", "w") as f:
        json.dump(r.json(), f)


def binance_connected_pairs():
    """
    Loads the pairs from Binance that have 3 or more connections

    :return: 'connected' pairs, e.g {USDT:[BTC,ETH], ETH:[ADA, OMG]}
    :rtype: {str : str list} dict
    """
    with open("pairs_list.json", "r") as f:
        pairs = json.load(f)
    binance_pairs = pairs["Data"]["Binance"]["pairs"]
    return {k: v for k, v in binance_pairs.items() if len(v) > 3}


def download_snapshot(pair_dict, outfolder):
    """
    Downloads a snapshot of bid/asks for a given dictionary of pairs,
    writes json to files.

    :param pair_dict: dict of pairs
    :type pair_dict: {str : str list}
    :param outfolder: name of folder to output to
    :type outfolder: str
    """
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    # Download data and write to files
    for p1, p2s in tqdm(pair_dict.items()):
        try:
            url = (
                f"https://min-api.cryptocompare.com/data/ob/l1/top?fsyms={p1}"
                + f"&tsyms={','.join(p2s)}&e=Binance&api_key="
                + AUTH
            )
            r = requests.get(url)
            with open(f"{outfolder}/{p1}_pairs_snapshot.json", "w") as f:
                json.dump(r.json(), f)
        except Exception as e:
            print(e)
            print("Failure for", p1)
            continue


def create_adj_matrix(pair_dict, snapshot_directory, outfile="snapshot.csv"):
    """
    Given a dict of pairs, create an adjacency matrix and populate it
    with snapshot data, processing bids and asks appropriately.
    The resulting adjacency matrix is a pandas df.

    e.g col BTC row ETH is how much ETH you get for 1 BTC
    e.g col ETH row BTC is how much BTC you get for 1 ETH

    :param pair_dict: dict of pairs
    :type pair_dict: {str : str list}
    :param outfile: name of output adjacency matrix file
    :type outfile: str
    """
    # Union of 'from' and 'to' pairs
    flatten = lambda l: [item for sublist in l for item in sublist]
    all_pairs = list(set(pair_dict.keys()).union(flatten(pair_dict.values())))

    # Create empty df
    df = pd.DataFrame(columns=all_pairs, index=all_pairs)

    for p1 in pair_dict.keys():
        with open(f"{snapshot_directory}/{p1}_pairs_snapshot.json", "r") as f:
            res = json.load(f)
        quotes = res["Data"]["RAW"][p1]
        for p2 in quotes:
            try:
                df[p1][p2] = float(quotes[p2]["BID"])
                df[p2][p1] = 1 / float(quotes[p2]["ASK"])
            except KeyError:
                print(f"Error for {p1}/{p2}")
                continue
    df.to_csv(outfile)


if __name__ == "__main__":
    if AUTH == "":
        with open("API_KEY.txt", "r") as f:
            AUTH = f.read()
    top_exchange_pairs()
    connected = binance_connected_pairs()
    print("Downloading snapshot...")
    download_snapshot(connected, "binance_data")
    print("Download finished. Creating adjacency matrix..")
    create_adj_matrix(connected, "binance_data")
