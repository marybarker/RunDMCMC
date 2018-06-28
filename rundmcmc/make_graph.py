from graph_tool import Graph
import pandas as pd
import geopandas as gp
<<<<<<< HEAD
import pysal
import json
from networkx.readwrite import json_graph
from shapely.ops import cascaded_union
<<<<<<< HEAD
import os.path
=======
import numpy as np
>>>>>>> ROUGH port to graph-tool

=======
import networkx
>>>>>>> Both networkx and graph-tool now return an np array of GEOIDs when nodes method is called

def get_list_of_data(filepath, col_name, geoid=None):
    """Pull a column data from a CSV file or any fiona-supported file.

    :filepath: Path to datafile.
    :col_name: List of column names to grab.
    :returns: List of data.

    """
    # Checks if you have inputed a csv or shp file then captures the data
    extension = os.path.splitext(filepath)

    if extension.lower() == "csv":
        df = pd.read_csv(filepath)
    else:
        df = gp.read_file(filepath)

    if geoid is None:
        geoid = "sampleIndex"
        df[geoid] = range(len(df))

    data = pd.DataFrame({geoid: df[geoid]})
    for i in col_name:
        data[i] = df[i]

    return data


def add_data_to_graph(df, graph, col_names):
    """Add columns of a dataframe to a graph using the the index as node ids.

    :df: Dataframe containing given columns.
    :graph: NetworkX graph containing appropriately labeled nodes.
    :col_names: List of dataframe column names to add.
    :returns: Nothing.

    """
    column_dictionaries = df[col_names].to_dict('index')
    networkx.set_node_attributes(graph, column_dictionaries)


def add_boundary_perimeters(graph, neighbors, df):
    """
    Add shared perimeter between nodes and the total geometry boundary.

    :graph: NetworkX graph.
    :neighbors: Adjacency information generated from pysal.
    :df: Geodataframe containing geometry information.
    :returns: The updated graph.

    """
    all_units = df['geometry']
    # creates one shape of the entire state to compare outer boundaries against
    boundary = gp.GeoSeries(cascaded_union(all_units).boundary)

    # finds if it intersects on outside and sets
    # a 'boundary_node' attribute to true if it does
    # if it is set to true, it also adds how much shared
    # perimiter they have to a 'boundary_perim' attribute
    for node in neighbors:
        graph.node[node]['boundary_node'] = boundary.intersects(
            df.loc[node, "geometry"]).bool()

        if boundary.intersects(df.loc[node, "geometry"]).bool():
            graph.node[node]['boundary_perim'] = float(
                boundary.intersection(df.loc[node, "geometry"]).length)

<<<<<<< HEAD
    return graph


def neighbors_with_shared_perimeters(neighbors, df):
    """Construct a graph with shared perimeter between neighbors on the edges.

    :neighbors: Adjacency information generated from pysal.
    :df: Geodataframe containing geometry information.
    :returns: NetworkX graph.

    """
    vtds = {}

    for shape in neighbors:
        vtds[shape] = {}

        for neighbor in neighbors[shape]:
            shared_perim = df.loc[shape, "geometry"].intersection(
                df.loc[neighbor, "geometry"]).length
            vtds[shape][neighbor] = {'shared_perim': shared_perim}
=======
    '''
    # Check to make sure there is a one-to-one between data and VTDs
    for i, _ in enumerate(data_name):
        if graph.num_vertices() != len(data[i]):
            raise ValueError("Your column length doesn't match the number of nodes!")

    # Adding data to the nodes
        for i, _ in enumerate(data_name):
            # get the graph-tool value type to create the property map for the data
            dtype = get_type(data[i][0])
            vdata = graph.new_vertex_property(dtype)

            # can't vectorize assignment of nonscalar data types
            if dtype == "string":
                for j in range(len(data[i])):
                    vdata[graph.vertex(i)] = data[i][j]
            else:
                # assign data as a vector, very slick
                graph.vertex_properties[data_name[i]] = vdata
                vdata.a = data[i]
<<<<<<< HEAD
            #graph.vertices[x][j] = data[i][x]
>>>>>>> ROUGH port to graph-tool

    return networkx.from_dict_of_dicts(vtds)

=======
>>>>>>> fix style and imports

def construct_graph_from_df(df, id_column=None, cols_to_add=None):
    """Construct initial graph from information about neighboring VTDs.

    :df: Geopandas dataframe.
    :returns: NetworkX Graph.

<<<<<<< HEAD
    """
    if id_column is not None:
        df = df.set_index(id_column)

    # Generate rook neighbor lists from dataframe.
    neighbors = pysal.weights.Rook.from_dataframe(
        df, geom_col="geometry").neighbors

    graph = neighbors_with_shared_perimeters(neighbors, df)

    add_boundary_perimeters(graph, neighbors, df)

    if cols_to_add is not None:
        add_data_to_graph(df, graph, cols_to_add)
=======
    '''
    graph = Graph()

    graph.add_vertex(len(lists_of_neighbors))
    # Creating the graph itself
    for vtd, list_nbs in enumerate(lists_of_neighbors):
        for d in list_nbs:
            e = graph.add_edge(graph.vertex(vtd), graph.vertex(d))

    shared_perim = graph.new_edge_property("double")
    graph.edge_properties["shared_perim"] = shared_perim
    # Add perims to edges
    for i, nbs in enumerate(lists_of_neighbors):
        for x, nb in enumerate(nbs):
            e = graph.edge(graph.vertex(i), graph.vertex(nb))
            graph.edge_properties["shared_perim"][e] = lists_of_perims[i][x]

    # Add GEOID to each node(VTD)
    vgeoid = graph.new_vertex_property("string")
    graph.vertex_properties["GEOID"] = vgeoid
    for i in range(len(geoid)):
        vgeoid[graph.vertex(i)] = geoid[i]
>>>>>>> ROUGH port to graph-tool

    return graph


def construct_graph_from_json(json_file):
    """Construct initial graph from networkx.json_graph adjacency JSON format.

    :json_file: Path to JSON file.
    :returns: NetworkX graph.

    """
    with open(json_file) as f:
        data = json.load(f)

    return json_graph.adjacency_graph(data)


def construct_graph_from_file(filename, id_column=None, cols_to_add=None):
    """Constuct initial graph from any file that fiona can read.

    This can load any file format supported by GeoPandas, which is everything
    that the fiona library supports.

    :filename: File to read.
    :id_column: Unique identifier column for the data units; used as node ids in the graph.
    :cols_to_add: List of column names from file of data to be added to each node.
    :returns: NetworkX Graph.

    """
    df = gp.read_file(filename)

    return construct_graph_from_df(df, id_column, cols_to_add)


def construct_graph(data_source, id_column=None, data_cols=None, data_source_type="fiona"):
    """
    Construct initial graph from given data source.

    :data_source: Data from which to create graph ("fiona", "geo_data_frame", or "json".).
    :id_column: Name of unique identifier for basic data units.
    :data_cols: Any extra data contained in data_source to be added to nodes of graph.
    :data_source_type: String specifying the type of data_source;
                       can be one of "fiona", "json", or "geo_data_frame".
    :returns: NetworkX graph.

    The supported data types are:

        - "fiona": The filename of any file that geopandas (i.e., fiona) can
                    read. This includes SHAPE files, GeoJSON, and others. For a
                    full list, check `fiona.supported_drivers`.

        - "json": A json file formatted by NetworkX's adjacency graph method.

        - "geo_data_frame": A geopandas dataframe.

    """
    if data_source_type == "fiona":
        return construct_graph_from_file(data_source, id_column, data_cols)

    elif data_source_type == "json":
        return construct_graph_from_json(data_source)

    elif data_source_type == "geo_data_frame":
        return construct_graph_from_df(data_source, id_column, data_cols)


def get_assignment_dict_from_df(df, key_col, val_col):
    """Grab assignment dictionary from the given columns of the dataframe.

    :df: Dataframe.
    :key_col: Column name to be used for keys.
    :val_col: Column name to be used for values.
    :returns: Dictionary of {key: val} pairs from the given columns.

    """
    dict_df = df.set_index(key_col)
    return dict_df[val_col].to_dict()


def get_assignment_dict_from_graph(graph, assignment_attribute):
    """Grab assignment dictionary from the given attributes of the graph.

    :graph: NetworkX graph.
    :assignment_attribute: Attribute available on all nodes.
    :returns: Dictionary of {node_id: attribute} pairs.

<<<<<<< HEAD
    """
    return networkx.get_node_attributes(graph, assignment_attribute)
=======
    :param graph: The graph object you are working on.
    :param cd_identifier: How the congressional district is labeled on your graph.
    :return: A dictionary.
    '''
    # creates a dictionary and iterates over the nodes to add node to CD.
    nodes = {}
    # get the vertex property map of the identifier
    vpop = graph.vertex_properties[cd_identifier]
    for i in range(graph.num_vertices()):
        nodes[i] = vpop[graph.vertex(i)]
    return nodes


def get_type(data):
    if isinstance(data, int) or isinstance(data, np.int64):  # type(data) == type(np.int64(2)):
        return "int"
    elif isinstance(data, float):
        return "float"
    elif isinstance(data, str):
        return "string"
    else:
        print(type(data))
        return "fail"
>>>>>>> ROUGH port to graph-tool
