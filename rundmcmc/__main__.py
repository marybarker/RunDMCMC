<<<<<<< HEAD
import sys
from rundmcmc.parse_config import read_basic_config
=======
from rundmcmc.ingest import ingest
from rundmcmc.make_graph import construct_graph, get_list_of_data, add_data_to_graph, pull_districts
from rundmcmc.validity import contiguous, Validator
from rundmcmc.partition import Partition, propose_random_flip
from rundmcmc.chain import MarkovChain
import time
>>>>>>> ROUGH port to graph-tool


def main(args=None):
    if not args:
        args = sys.argv
    if len(args) < 1:
        raise ValueError("no config file provided")

    chain, chain_func, scores, output_func, output_type = read_basic_config(args[1])
    print("setup the chain")

    output = chain_func(chain)
    print("ran the chain")

<<<<<<< HEAD
    output_func(output, scores, output_type)


if __name__ == "__main__":
    main(sys.argv)
=======
    assignment = pull_districts(graph, 'CD')
    validator = Validator([contiguous])

    initial_partition = Partition(graph, assignment, aggregate_fields=['ALAND'])
    accept = lambda x: True

    n = 2**15
    chain = MarkovChain(propose_random_flip, validator, accept, initial_partition, total_steps=n)

    i = 0
    print("starting")
    start = time.time()
    for step in chain:
        # print(step.assignment)
        if i % 2**10 == 0:
            print(i)
        i += 1
    print(time.time() - start)


if __name__ == "__main__":
    import sys
    sys.path.append('/usr/local/Cellar/graph-tool/2.26_2/lib/python3.6/site-packages/')
    main()
>>>>>>> ROUGH port to graph-tool
