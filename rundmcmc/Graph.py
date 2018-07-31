import networkx as nx
import graph_tool.all as gta
import pandas as pd
import geopandas as gp
import numpy as np
import warnings
import os.path
#import rundmcmc.networkx_graph_helpers as nx_graph
import networkx_graph_helpers as nx_graph

class VisitorExample(gta.BFSVisitor):

    def __init__(self):
        self.counter = 0

    def discover_vertex(self, u):
        self.counter += 1

    def __len__(self):
        return self.counter

class Graph:
    """
        This class is an abstraction layer that sits in between NetworkX (or
        graph-tool) and the rest of the program.

        TODO Figure out which methods run faster at scale. Currently, getting
        vertices and edges are faster with graph-tool, but NetworkX has the
        upper hand on getting node attributes and neighbors.
    """

    def __init__(self,
            path=None,
            unique_id_col=None,
            area_col=None,
            population_col=None,
            district_col=None,
            data_cols=None,
            data_source_type='fiona',
            graph_tool=False):
        """
            Main properties of the Graph instance.
                :library:   String denoting which graph implementation library
                            is being used.
                :graph:     Graph object.
                :path:      Path to the source file of the graph.
        """
        self.library = "graph_tool" if graph_tool else "networkx"
        self.graph = None
        self.path = None
        self.id = unique_id_col
        self.area = area_col
        self.population = population_col
        self.district = district_col


        """
            Internal properties:
                :_converted:    Has this graph been converted to graph-tool?
                :_data_added:   Has data been added to this graph?
                :_xml_location: GraphML filepath.
                :nodes:         Dataframe indexed on Netowrkx node ID with attributes as columns
                :nodenames:     dictionary of nodeindex to Networkx node ID
                :nodeindex:     dictionary of Networkx node ID to nodeindex
                :edges:         dictionary of edges with node endpoints and edge attributes
        """
        self._converted = False
        self._data_added = False
        self._xml_location = None
        self.nodeindex = None
        self.nodenames = None
        self.nodes = None
        self.edges = None

        # Try to make a graph if `path` is provided.
        if path:
            self.graph = nx_graph.construct_graph(
                    path, unique_id_col, population_col, area_col,
                    district_col, data_cols, data_source_type)
            self.nodes = self.graph.nodes
            self.edges = self.graph.edges
            self.nodeindex = dict(zip(list(self.graph.nodes), range(len(self.graph.nodes))))

    def __del__(self):
        """
            Removes a file if a converted graph exists so there aren't any
            artifacts.
        """
        if self._xml_location:
            os.remove(self._xml_location)

    def set_node_attributes(self, column_dict=None, values=None, name=None):
        """Add data to nodes on graph. Mimics networkx.set_node_attributes()

            :column_dict: (option 1) dictionary keyed on nodes,
                            with values that are of the form: 
                            {"attribute_name": attribute_value}

            :values: (option 2) list of values to add (same order as the nodes)
            :name:   (option 2) name of the attribute saved in `values` list
        """
        if self._converted:
            nx.set_node_attributes(self.graph, column_dict, values=values, name=name)
        else:
            if column_dict is not None:
                data = pd.DataFrame(column_dict)
                self._nodedata = self._nodedata.merge(data)
            elif (values is not None) and (name is not None):
                self._nodedata[name] = map(values.get, self._nodename)

    def add_data_to_graph(self, df, col_names, id_col=None):
        """Add columns of a dataframe to a graph using the the index as node ids.

            :df: Dataframe containing given columns.
            :col_names: List of dataframe column names to add.
            :id_col: column in df with id that matches self.unique_id_col

            NOTE: if id_col=None, then it is assumed that df has rows listed
            in the same order as the nodes on the graph, and adds attributes
            with that order.
        """
        if id_col:
            indexed_df = df.set_index(id_col)
        else:
            indexed_df = df

        column_dictionaries = indexed_df[col_names].to_dict('index')
        self.set_node_attributes(column_dictionaries)

    def convert(self):
        """
            Converts an existing NetworkX graph to graph-tool. This method uses
            a simple XML write/read; i.e. NetworkX writes the graph to XML in a
            format readable by graph-tool. Additionally, the XML file that's
            written is available for the life of the Graph instance, then thrown
            out afterward.

            TODO See if we can write to a buffer/stream instead of a file... that
            may prove faster.

            TODO Do a user's permissions affect this program's ability to write
            in the directory where it's installed? Currently, the XML file is
            being created in the *user's* current working directory, not where
            the RunDMCMC is put... might be worth looking into.

            TODO Discuss if there should be a flag (--preserve-conversion, maybe)
            to not delete the XML file when this object is garbage-collected. If
            a user is running a bunch of chains and getting their adjacency (and
            other) data from, say, a GeoJSON file, and they're using graph-tool,
            wouldn't it make sense to provide them with an option to not have to
            re-convert each time? I feel this is something to address.
        """
        # Check that the user actually wants to convert to graph-tool.
        if self.library != "graph-tool":
            # Try to convert the graph to GraphML
            try:
                self._xml_location = os.getcwd() + "/graph.xml"
                nx.write_graphml_xml(self.graph, (self._xml_location))
                self.graph = gta.load_graph(self._xml_location)
                self._converted = True
                self.library = "graph_tool"
                nodeNameType = type(list(self.nodes.keys())[0])
                old_edge_keys = list(self.edges)

                _nodedata = {
                    x: list(y) for x, y in list(self.graph.vertex_properties.items())
                }
                _nodename = map(nodeNameType,
                        list(self.graph.vertex_properties['_graphml_vertex_id']))

                # access a node's properties by:
                #    self._nodes['propertyname']['nodename']
                self.nodes = pd.DataFrame(_nodedata)
                self.nodes['node_index'] = range(len(self.nodes))

                # number of nodes in graph
                self._num_nodes = len(self.nodes)

                # acces a node's index by:
                #    self._nodeindex[nodename]
                self.nodenames = dict(enumerate(_nodename))
                self.nodeindex = dict(zip(
                    list(self.nodenames.values()), list(self.nodenames.keys())
                    ))
                # make sure the node name in graphtool graph is of same datatype as nx graph
                self.nodes['unique'] = self.nodes['_graphml_vertex_id'].astype(nodeNameType)
                self.nodes = self.nodes.set_index('unique').to_dict('index')

                # access edge properties by:
                #    self.edges[edgename]['propertyname']
                self.edges = {
                    x: list(y) for x, y in list(self.graph.edge_properties.items())
                }
                self.edges = pd.DataFrame(self.edges)
                endpoints = [tuple(x) for x in
                        np.vectorize(self.nodenames.get)(np.asarray(self.graph.get_edges())[:,:2])]
                self.edges['endpoints'] = [tuple(sorted([str(x[0]), str(x[1])])) for x in endpoints]
                self.edges = self.edges.set_index('endpoints')
                """
                # now add the edges to the dataframe with node order of each tuple reversed
                _reversed_order = self.edges.copy(deep=True)
                _reversed_order.index = map(lambda x: (x[1], x[0]), _reversed_order.index.tolist())
                self.edges = self.edges.append(_reversed_order)
                self.edges = self.edges.loc[old_edge_keys].to_dict('index')
                """
                self.edges = self.edges.to_dict('index')
                self.visitor = VisitorExample()

                return self.graph
            except:
                err = "Encountered an error during conversion. Aborting."
                raise RuntimeError(err)
                return

    def is_connected(self, nodes=None):
        if not self._converted:
            if not nodes:
                nodes = self.graph.nodes
            adj = nx.to_dict_of_lists(self.graph, nodes)
            return nx_graph._bfs(adj)
        else:
            if not nodes:
                tmp = self.graph
            else:
                tmp = self.subgraph(nodes)

            visitor = self.visitor
            visitor.counter=0
            gta.bfs_search(tmp, tmp.get_vertices()[0], visitor=visitor)
            return visitor.counter == len(tmp.get_vertices())

    def neighbors(self, node):
        """
            Return neighbors of a node
        """
        if not self._converted:
            return np.asarray(list(nx.all_neighbors(self.graph, node)))
        else:
            nodeidx = self.nodeindex[node]
            return map(self.nodenames.get, self.graph.vertex(nodeidx).all_neighbors())

    def subgraph(self, nodes):
        """
            Finds the subgraph containing all nodes in `nodes`.
        """
        if not self._converted:
            return self.graph.subgraph(nodes)
        else:
            vfilt = np.zeros(self._num_nodes, dtype=bool)
            nodes = list(map(self.nodeindex.get, nodes))
            vfilt[nodes] = True
            return gta.GraphView(self.graph, vfilt=vfilt)


if __name__ == "__main__":
    g = Graph("./testData/MO_graph.json")
    g.nodes
