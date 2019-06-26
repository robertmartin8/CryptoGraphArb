import pandas as pd
import numpy as np
import networkx as nx
import math
from collections import defaultdict


def bellman_ford_return_cycle(g, s):
    """
    Bellman Ford, modified so that it returns cycles.
    Runtime is O(E^2).
    
    :param g: graph
    :type g: networkx weighted DiGraph
    :param s: source vertex
    :type s: str
    :return: a negative-weight cycle (if it exists)
    :rtype: str list
    """
    n = len(g.nodes())
    d = defaultdict(lambda: math.inf)  # distances dict
    p = defaultdict(lambda: -1)  # predecessor dict
    d[s] = 0

    for _ in range(n - 1):
        for u, v in g.edges():
            # Bellman-Ford relaxation
            weight = g[u][v]["weight"]
            if d[u] + weight < d[v]:
                d[v] = d[u] + weight
                p[v] = u  # update pred

    # Find cycles if they exist
    all_cycles = []
    for u, v in g.edges():
        weight = g[u][v]["weight"]
        # If we can relax further, there must be a neg-weight cycle
        if d[u] + weight < d[v]:
            cycle = []
            x = v
            while True:
                # Walk back along predecessors until a cycle is found
                cycle.append(x)
                x = p[x]
                if x == v or x in cycle:
                    break
            # Slice to get the cyclic portion
            idx = cycle.index(x)
            cycle.append(x)
            all_cycles.append(cycle[idx:][::-1])

    # Filter to get unique cycles
    return [list(i) for i in set(tuple(j) for j in all_cycles)]


def get_all_negative_cycles(g):
    """
    Get all negative-weight cycles by calling Bellman-Ford on
    each vertex. O(VE^2)
    
    :param g: graph
    :type g: networkx weighted DiGraph
    :return: list of negative-weight cycles
    :rtype: list of str list
    """
    all_paths = []
    for v in g.nodes():
        all_paths.append(bellman_ford_return_cycle(g, v))
    flatten = lambda l: [item for sublist in l for item in sublist]
    return [list(i) for i in set(tuple(j) for j in flatten(all_paths))]


def calculate_arb(cycle, g, verbose=True):
    """
    For a given negative-weight cycle on the log graph, calculate and
    print the arbitrage
    
    :param cycle: the negative-weight cycle
    :type cycle: list
    :param g: graph
    :type g: networkx weighted DiGraph
    :param verbose: whether to print path and arb
    :type verbose: bool
    :return: fractional value of the arbitrage
    :rtype: float
    """
    total = 0
    for (p1, p2) in zip(cycle, cycle[1:]):
        total += g[p1][p2]["weight"]
    arb = np.exp(-total) - 1
    if verbose:
        print("Path:", cycle)
        print(f"{arb*100:.2g}%\n")
    return arb


def find_arbitrage(filename="snapshot.csv", find_all=False, sources=None):
    """
    Looks for arbitrage opportunities within a snapshot, i.e negative-weight cycles
    that include the currencies given in the sources list
    
    :param filename: filename of snapshot, defaults to "snapshot.csv"
    :type filename: str, optional
    :param find_all: whether to find all paths, defaults to False.
                     If false, sources must be provided.
    :type find_all: bool, optional
    :param sources: list of starting nodes – should choose the 'most connected' pairs, 
                    defaults to None.
    :type sources: str list, optional
    :return: list of negative-weight cycles, or None if none exist 
    :rtype: str list
    """
    # Read df and convert to negative logs so we can use Bellman Ford
    # Negative weight cycles thus correspond to arbitrage opps
    df = pd.read_csv(filename, header=0, index_col=0)
    log_df = -np.log(df).fillna(0)

    # Transpose log_df so that graph has same API as the dataframe
    g = nx.DiGraph(log_df.T)

    if nx.negative_edge_cycle(g):
        print("ARBITRAGE FOUND\n" + "=" * 15 + "\n")

        all_paths = []
        if find_all:
            unique_cycles = get_all_negative_cycles(g)
        else:
            for s in sources:
                all_paths.append(bellman_ford_return_cycle(g, s))
            flatten = lambda l: [item for sublist in l for item in sublist]
            unique_cycles = [list(i) for i in set(tuple(j) for j in flatten(all_paths))]

        for p in unique_cycles:
            calculate_arb(p, g)
        return unique_cycles

    else:
        print("No arbitrage opportunities")
        return None


if __name__ == "__main__":
    find_arbitrage(sources=["BTC", "USDT", "ETH", "BNB"])

