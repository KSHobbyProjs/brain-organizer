# semantic_search.py
# A module to search an embedding space for embeddings most similar to a query
# using cosine similarity.
# currently acts mainly as a wrapper around sklearn kNN.

from dataclasses import dataclass
import numpy as np

from sklearn.neighbors import NearestNeighbors

@dataclass
class SearchResult:
    embedding_idx: int
    score: float 
    # embedding: np.ndarray maybe it needs this in the future

class SemanticSearcher: 
    def __init__(self, embeddings: np.ndarray, metric='cosine'):
        """
        Takes a list of embeddings, finds the top embeddings
        closest to query embedding.
        
        Parameters
        ----------
        embeddings : np.ndarray
            Shape (n, d). Matrix of n embedding vectors.
        """

        self.embeddings = embeddings
        self.nn = NearestNeighbors(metric=metric).fit(embeddings)

    def search(self, query: np.ndarray, k: int | None = None) -> list[SearchResult]:
        """
        Finds the k embeddings closest to the query embedding based on some metric (cosine).
        If k is None, returns all embeddings ranked by similarity.

        Parameters
        ----------
        query : np.ndarray
            Embedded query text. Shape (d,) for d features.
        k : int
            Number of neighbors to find. Default is all.

        Results
        -------
        retrieved_results : list[SearchResult]
            List of k nearest neighbors and the distance to them.

        Notes
        -----
        This function assumes that query is a single embedded vector.
        """
        if k is None:
            k = len(self.embeddings)
        # compute k nearest neighbors 
        distances, top_k_idx = self.nn.kneighbors(query.reshape(1, -1), n_neighbors=k, return_distance=True)
        
        # sklearn returns results with shape (query_count, neighbor_count)
        # sklearn cosine distance = 1 - cosine similarity
        # convert distances back to similarity score
        scores = 1 - distances[0]  
        top_k_idx = top_k_idx[0]
        
        retrieved_results = [
                SearchResult(
                    embedding_idx=idx,
                    score=scores[i],
                    )
                for i, idx in enumerate(top_k_idx)
                ]
        return retrieved_results


    """ DEPRECATED """
    """
    def search(self, query: np.ndarray, k: int=1) -> list[SearchResult]:
        from .utils import cosine_similarity_to_group
        scores = cosine_similarity_to_group(query, self.embeddings)
        top_k_idx = np.argsort(scores)[::-1][:k]

        retrieved_results = [
                SearchResult(
                        embedding_idx = idx,
                        score=scores[idx],
                        #embedding = self.embeddings[idx],
                        )
                for idx in top_k_idx
                ]

        return retrieved_results
    """
