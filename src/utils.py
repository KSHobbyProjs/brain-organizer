# utils.py
# util methods shared by many classes

"""
Apart from numpy_to_python, these functions are no longer used throughout the program. 
sklearn already has methods which circumvent the need for these methods.

These are kept here for posterity.
"""

import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings a and b

    Parameters
    ----------
    a : np.ndarray
    b : np.ndarray
        The embeddings which to compare.

    Returns
    -------
    similarity : float
        The cosine similarity between embeddings a and b.
    """
    # normalize
    a, b = a/np.linalg.norm(a), b/np.linalg.norm(b)
    similarity = a @ b
    return similarity

def cosine_similarity_to_group(query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between a query vector and a group of embeddings.

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

def cosine_similarity_mat(embeddings: np.ndarray) -> np.ndarray:
    """
    Compute the cosine similarity between all pairs of embeddings.

    Parameters
    ----------
    embeddings : np.ndarray
        Array of embeddings. Shape (n, d) for n embeddings of dimension d.
        
    Returns
    -------
    scores : np.ndarray
        Array of similarity scores between all embeddings. Shape (n, n).
    """
    # normalize all embeddings
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    # compute E @ E.T (memory hog oink oink)
    # scores is symmetric, but E @ E.T is still faster than manual looping 
    scores = embeddings @ embeddings.T
    return scores

def compute_centroid(embeddings: np.ndarray) -> np.ndarray:
    """ 
    Compute the centroid of a given set of embeddings.

    Parameters
    ---------
    embeddings : np.ndarray
        Array of embeddings. Shape (n_embeddings, n_features).

    Returns
    -------
    np.ndarray
        Centroid of embeddings. Shape (n_features,)
    """
    return np.mean(embeddings, axis=0)

def numpy_to_python(obj): 
    """ 
    Recursively move through obj and convert all
    numpy types to python-native types
    """
    if isinstance(obj, np.generic):
        # np.float32, np.float64, np.int32, np.bool_, etc.
        return obj.item()

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    if isinstance(obj, dict):
        return {k: numpy_to_python(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [numpy_to_python(v) for v in obj]

    if isinstance(obj, tuple):
        return tuple(numpy_to_python(v) for v in obj)

    return obj
