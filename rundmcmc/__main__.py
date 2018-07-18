import sys
from rundmcmc.parse_config import read_basic_config
from rundmcmc.ingest import ingest
from rundmcmc.make_graph import construct_graph, get_list_of_data, add_data_to_graph, pull_districts
from rundmcmc.validity import contiguous, Validator
from rundmcmc.partition import Partition, propose_random_flip
from rundmcmc.chain import MarkovChain
import time


def main(args=None):
    if not args:
        args = sys.argv
    if len(args) < 1:
        raise ValueError("no config file provided")

    chain, chain_func, scores, output_func, output_type = read_basic_config(args[1])
    print("setup the chain")

    output = chain_func(chain)
    print("ran the chain")

    output_func(output, scores, output_type)


if __name__ == "__main__":
    main(sys.argv)
