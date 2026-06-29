# semantic_search.py
# A module for using pre-trained sentence transformers to search for semantic
# meaning among embedded text. Takes as input embedded text and returns the 
# domain object (Note) that most closely aligns with it.

from dataclasses import dataclass
import numpy as np

from .parser import Note

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
    note: Note
    score: float
    index: int

class SemanticSearcher: 
    def __init__(self, embeddings: np.ndarray, notes: list[Note]):
        """
        Notes
        -----
        The embeddings matrix should be ordered. I.e., structured so
        that the ith row corresponds to the embedding vector for note notes[i]
        """

        self.embeddings = embeddings
        self.notes = notes

    def search(self, query: np.ndarray, k: int=1) -> list[SearchResult]:
        scores = cosine_similarity(query, self.embeddings)
        top_k_idx = np.argsort(scores)[::-1][:k]

        retrieved_notes = [
                SearchResult(
                        note=self.notes[idx],
                        score=scores[idx],
                        index=idx
                        )
                for idx in top_k_idx
                ]

        return retrieved_notes
        
