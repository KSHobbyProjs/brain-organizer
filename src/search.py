# semantic_search.py
# A module for using pre-trained sentence transformers to search for semantic
# meaning among embedded text. Takes as input embedded text and returns the 
# domain object (Note) that most closely aligns with it.

# EDIT: Since changed to no longer depend on Note (coupling made troubleshooting difficult)

from dataclasses import dataclass
import numpy as np


def cosine_similarity(query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between a query vector and a matrix of embeddings.

    Parameters
    ------
    query : np.ndarray
        Shape (d,). Embedded query vector.
    embeddings : np.ndarray
        Shape (n, d). Matrix of n embedding vectors.
    
    Returns
    ------
    np.ndarray
        Shape (n,). Cosine similarity between query and each embedding.

    Notes
    -----
    Cosine similarity is defined as:
        sim(a, b) = (a . b) / (||a|| ||b||)

    This implementation assumes inputs are not necessarily normalized.
    """
    # normalize query and embeddings
    query = query / np.linalg.norm(query)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    # compute dot product of normalized query and embedding vector
    scores = embeddings @ query
    return scores

@dataclass
class SearchResult:
    embedding_idx: int
    score: float 
    # embedding: np.ndarray maybe it needs this in the future

class SemanticSearcher: 
    def __init__(self, embeddings: np.ndarray):
        """
        Takes a list of embeddings, finds the top closest embeddings
        closest to query embedding.
        
        Parameters
        ----------
        embeddings : np.ndarray
            Shape (n, d). Matrix of n embedding vectors.
        """

        self.embeddings = embeddings

    def search(self, query: np.ndarray, k: int=1) -> list[SearchResult]:
        scores = cosine_similarity(query, self.embeddings)
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
        
