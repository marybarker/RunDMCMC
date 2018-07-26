from rundmcmc.Graph import Graph


def test_graph_abstraction_setup():
    filepath = "./data/test/testData.shp"
    filetype = "fiona"
    geo_id = "id"
    pop_col = "POP"
    dist_col = "CD"
    data = ["USH_DV08", "USH_RV08"]

    # test graph generation from a shapefile
    mygraph = Graph(filepath, unique_id_col=geo_id, population_col=pop_col,
            district_col=dist_col, data_cols=data, data_source_type=filetype) 

    # save edges, nodes, and sample neighbor to test that conversion works
    oldEdges = dict(mygraph.edges)
    oldNodes = dict(mygraph.nodes(data=True))
    oldNeighbors = mygraph.neighbors(list(mygraph.nodes)[0])

    # validate convert working
    mygraph.convert()

    # new edges, nodes, and sample neighbor for comparison with old
    newEdges = dict(mygraph.edges)
    newNodes = dict(mygraph.nodes)
    newNeighbors = mygraph.neighbors(list(mygraph.nodes)[0])

    # make sure converted values match old, and that the structues work the same
    for edge in oldEdges:
        for key in oldEdges[edge].keys():
            assert oldEdges[edge][key] == newEdges[edge][key]

    for node in oldNodes:
        for key in oldNodes[node].keys():
            assert oldNodes[node][key] == newNodes[node][key]
