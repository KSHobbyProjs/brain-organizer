# graph.py
# a class to handle the graph of topics

import networkx as nx
import numpy as np
from sklearn.neighbors import NearestNeighbors


# TODO: Possibly pass the metric model ('cosine') in as an argument.
# TODO: Possibly restructure so GraphBuilder and Searcher don't have to both
#       instantiate a NearestNeighbor object

class SemanticGraphBuilder:
    def __init__(self, embeddings: np.ndarray):
        """
        Produces a graph for given embeddings

        """
        self.graph = nx.Graph()
        self.embeddings = embeddings

        self.nn = NearestNeighbors(metric='cosine').fit(embeddings)

    def create_hairball_graph(self) -> None:
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
            self.graph.add_node(i)
            for j in range(i+1, num_embeddings):
                self.graph.add_edge(i, j, weight=score_mat[i,j]) 

    def create_knn_graph(self, k: int=5) -> None:
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
            self.graph.add_node(i) # add each embedding as a node
            edges = [(i, j, score) for j, score in zip(top_k_idx, scores[i,:])] # create edges between embedding and its neighbors
            self.graph.add_weighted_edges_from(edges)

    def create_mutual_knn_graph(self, k: int=5) -> None:
        """
        Creates a graph where embeddings are nodes and node i
        and node j are connected with an edge if both nodes are
        members of the kNN of the other.
        """
        # grab top k neighbors for all embeddings
        distances, neighbors_idx = self.nn.kneighbors(self.embeddings, n_neighbors=k, return_distance=True)
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

        # add nodes and edges
        for i in range(n):
            self.graph.add_node(i)  # add each embedding as a node 
            for j, score in neighbor_lookup[i].items():
                # add an edge if embeddings are neighbors to each other
                if i in neighbor_sets[j]:
                    self.graph.add_edge(i, j, weight=score) 
    
    def create_threshold_graph(self, threshold: float=.5) -> None:
        """
        Creates a graph where embeddings are nodes and node i and
        node j are connected only if they have a score > threshold
        """
        # get neighbors with similarity score >= threshold for all embeddings
        distances, neighbors_idx = self.nn.radius_neighbors(radius=1-threshold, return_distance=True) 
        scores = 1 - distances

        # add nodes and edges
        for i in range(len(self.embeddings)):
            self.graph.add_node(i) # add each embedding as a node
            edges = [(i, j, score) for j, score in zip(neighbors_idx[i], scores[i])]
            self.graph.add_weighted_edges_from(edges)
