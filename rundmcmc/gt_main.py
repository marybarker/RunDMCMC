#from rundmcmc.Graph import Graph
from newGraph import Graph

from rundmcmc.partition import Partition
from rundmcmc.updaters import (Tally, boundary_nodes, cut_edges,
                               cut_edges_by_part,
                               exterior_boundaries, interior_boundaries,
                               perimeters)
from rundmcmc.updaters import polsby_popper
from rundmcmc.updaters import votes_updaters
from rundmcmc.defaults import BasicChain
from rundmcmc.make_graph import construct_graph, add_data_to_graph
from time import time
from rundmcmc.run import pipe_to_table

from validity import (L1_reciprocal_polsby_popper, UpperBound,
                               Validator, no_vanishing_districts,
                               refuse_new_splits, contiguous, fast_connected,
                               proposed_changes_still_contiguous,
                               within_percent_of_ideal_population)
"""
from rundmcmc.validity import (L1_reciprocal_polsby_popper, UpperBound,
                               Validator, no_vanishing_districts,
                               refuse_new_splits, contiguous, fast_connected,
                               proposed_changes_still_contiguous,
                               within_percent_of_ideal_population)
"""

from rundmcmc.proposals import \
    propose_random_flip_no_loops as propose_random_flip
from rundmcmc.accept import always_accept
from rundmcmc.chain import MarkovChain
import geopandas as gp

default_constraints = [#fast_connected,
                       proposed_changes_still_contiguous,
                       #contiguous,
                       no_vanishing_districts,
                       refuse_new_splits]


def main():
    dataCols = ['USH_DV08', 'USH_RV08']

    df = gp.read_file('./testData/mo_cleaned_vtds.shp')

    G = Graph('./testData/with_cd_plan.json',
            geoid_col='GEOID10',
            area_col='ALAND10',
            pop_col='POP100',
            district_col='CD',
            data_cols=dataCols)

    print([x for x in G.graph.neighbors(list(G.graph.nodes())[0])])

    add_data_to_graph(df, G, col_names=dataCols, id_col="GEOID10")

    assignment = dict([(x, G.graph.nodes[x]['CD']) for x in G.graph.nodes])#zip(G.nodes, G.node_properties('CD')))

    updaters = {
        **votes_updaters(['USH_DV08', 'USH_RV08']),
        'population': Tally('POP100', alias='population'),
        'perimeters': perimeters,
        'exterior_boundaries': exterior_boundaries,
        'interior_boundaries': interior_boundaries,
        'boundary_nodes': boundary_nodes,
        'cut_edges': cut_edges,
        'areas': Tally('ALAND10', alias='areas'),
        'polsby_popper': polsby_popper,
        'cut_edges_by_part': cut_edges_by_part
    }

    G.convert()
    print([x for x in G.graph.neighbors(list(G.graph.nodes())[0])])

    p = Partition(G.graph, assignment, updaters)

    validator = Validator(default_constraints)

    chain = MarkovChain(propose_random_flip, validator, always_accept, initial_state=p, total_steps=30)

    print("MADE THE CHAIN")
    print(":) ")
    print(":-0")
    print(":-|")
    print(":-<")

    for step in chain:
        print(chain.counter)
    print("All done using ", default_constraints[0])

if __name__ == "__main__":
    import sys
    sys.path.append('/usr/local/Cellar/graph-tool/2.26_2/lib/python3.6/site-packages/')
    main()
