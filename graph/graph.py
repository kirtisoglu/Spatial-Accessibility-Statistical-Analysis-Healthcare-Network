"""    
This module provides tools for working with graphs in the context of geographic data.
It extends the functionality of the NetworkX library, adding support for spatial data structures,
geographic projections, and serialization to and from JSON format.

Note:
This module relies on NetworkX, pandas, and geopandas, which should be installed and imported as required.
"""



import json

import networkx
from networkx.readwrite import json_graph
import pandas as pd




class Graph(networkx.Graph):
    """
    Represents a dual graph of a geographical region, extending the :class:`networkx.Graph`.

    This class includes class methods for constructing graphs from shapefiles, and for saving 
    and loading graphs in JSON format.
    """


    def __repr__(self):
        return "<Graph [{} nodes, {} edges]>".format(len(self.nodes), len(self.edges))
    

    @classmethod
    def from_json(cls, json_file: str) -> "Graph":
        """
        Load a graph from a JSON file in the NetworkX json_graph format.

        :param json_file: Path to JSON file.
        :type json_file: str

        :returns: The loaded graph as an instance of this class.
        :rtype: Graph
        """
        with open(json_file) as f:
            data = json.load(f)
        g = json_graph.adjacency_graph(data)
        graph = cls.from_networkx(g)
        graph.issue_warnings()
        return graph