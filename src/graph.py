# graph.py
# a class to handle the graph of topics

import networkx as nx
import numpy as np
from sklearn.neighbors import NearestNeighbors

from functools import wraps

"""
A class that owns a graph given embeddings as nodes.
"""

# TODO: (NOT NECESSARY; KEPT FOR POSTERITY) Possibly restructure so GraphBuilder and Searcher don't have to both
#       instantiate a NearestNeighbor object

class SemanticGraphBuilder:
    def __init__(self, embeddings: np.ndarray, metric: str='cosine', seed=42):
        """
        Produces a graph for given embeddings
        """
        self.graph = nx.Graph()
        self.embeddings = embeddings
        self.seed = seed

        self.nn = NearestNeighbors(metric=metric).fit(embeddings)

        # add one node for each embedding (labeled by embedding id) to the graph
        self._initialize_nodes() 
        self._num_nodes: int = len(embeddings)
        self._num_edges: int | None = None

    # -------------------------------------- Create Graph Methods ------------------------------------------------------------
    def create_hairball_graph(self) -> nx.Graph:
        """ 
        Creates a graph where all nodes are connected to all other nodes
        with a weight determined by the cosine similarity between embeddings.

        Note
        ----
        Not recommended unless the number of embeddings is small. 
        """
        from .utils import cosine_similarity_mat # the one kept use of the since deprecated utils.py functions

        # grab similarity matrix between all embeddings. Shape (n_embeddings, n_embeddings)
        score_mat = cosine_similarity_mat(self.embeddings)

        num_embeddings = len(self.embeddings)
        for i in range(num_embeddings-1):
            for j in range(i+1, num_embeddings):
                self.graph.add_edge(i, j, weight=score_mat[i,j]) 
        return self.graph

    def create_knn_graph(self, k: int=5) -> nx.Graph:
        """
        Creates a graph where embeddings are nodes and node i
        is connected to node j with an edge if j is in the kNN
        of node i.
        """
        # grab top k neighbors of each embedding
        # (kneighbors already ensures no embedding is its own neighbor, so no masking logic needed)
        distances, neighbors_idx = self.nn.kneighbors(n_neighbors=k, return_distance=True)
        scores = 1 - distances
        
        for i in range(len(self.embeddings)):
            # grab top k neighbors for embedding i
            top_k_idx = neighbors_idx[i, :]
            
            # add nodes and edges
            edges = [(i, j, score) for j, score in zip(top_k_idx, scores[i,:])] # create edges between embedding and its neighbors
            self.graph.add_weighted_edges_from(edges)
        return self.graph

    def create_mutual_knn_graph(self, k: int=5) -> nx.Graph:
        """
        Creates a graph where embeddings are nodes and node i
        and node j are connected with an edge if both nodes are
        members of the kNN of the other.
        """
        # grab top k neighbors for all embeddings
        distances, neighbors_idx = self.nn.kneighbors(n_neighbors=k, return_distance=True)
        scores = 1 - distances

        # get neighbors for each embedding (neighbor_sets[i] are the neighbor idxs for embedding i)
        # (neighbor_lookup[i] is a dictionary with keys=neighbor idxs for embedding i and values=scores)
        neighbor_sets, neighbor_lookup = [], []
        n = len(self.embeddings)
        for i in range(n):
            k_neighbors = neighbors_idx[i, :]
            k_scores = scores[i, :]
            neighbor_sets.append(set(k_neighbors)) # make it a set so lookup is O(1)
            neighbor_lookup.append(dict(zip(k_neighbors, k_scores)))

        # add edges
        for i in range(n):
            for j, score in neighbor_lookup[i].items():
                # add an edge if embeddings are neighbors to each other
                if i in neighbor_sets[j]:
                    self.graph.add_edge(i, j, weight=score) 
        return self.graph
    
    def create_threshold_graph(self, threshold: float=.5) -> nx.Graph:
        """
        Creates a graph where embeddings are nodes and node i and
        node j are connected only if they have a score > threshold
        """
        # get neighbors with similarity score >= threshold for all embeddings
        distances, neighbors_idx = self.nn.radius_neighbors(radius=1-threshold, return_distance=True) 
        scores = 1 - distances

        # add nodes and edges
        for i in range(len(self.embeddings)):
            edges = [(i, j, score) for j, score in zip(neighbors_idx[i], scores[i])]
            self.graph.add_weighted_edges_from(edges)
        return self.graph

    def _initialize_nodes(self):
        """ Add one node for every embedding """
        for i in range(len(self.embeddings)):
            self.graph.add_node(i)

    # ------------------------------------------------------------ Stat / Analysis Methods --------------------------------
    # find communities in the graph structure using Louvain
    def label_communities(self, resolution=1) -> list[set]:
        # TODO: add method as an argument so Louvain isn't the only possibility
        # TODO: implement hierarchical structure by repeatedly running Louvain
        #       at different resolutions.
        """
        Gets communities of a graph using Louvain. Louvain works by maximizing
        modularity. Modularity is the probability that a randomly selected node
        lies in the cluster minus the probability that a randomly selected node
        lies in the cluster given that edges are distributed randomly. 

        Louvain works in two phases:
        (1) assigns each node it's own community,
        greedily moving each node to neighborhing communities to find optimal
        modularity increase. Repeating until no move increases modularity.
        (2) Create a new graph with nodes being the current communitites, and repeat
        phase one.

        Parameters
        ----------
        resolution: int, optional
            Default is 1. Any resolution lower than 1 favors
            larger communities (coarse). Any resolution higher 
            than 1 favors smaller communities (fine)

        Returns
        -------
        list[set]
            The list of sets where each set includes all nodes in a given cluster.
        """
        communities = nx.community.louvain_communities(
                        G=self.graph,
                        seed=self.seed,
                        resolution=resolution,
                        weight="weight"
                    )
        
        for i, community in enumerate(communities):
            for node in community:
                self.graph.nodes[node]["community_id"] = i

        return communities 

    # get nodes forming a hierarchy structure in the graph
    def get_hierarchy(self):
        pass

    # get bridge nodes / nodes that connect many groups
    def get_betweeness_centrality(self):
        pass

