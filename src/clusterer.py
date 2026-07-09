# clustering.py
# A class for clustering embedded notes

import numpy as np
from sklearn.cluster import KMeans

# Add Cluster data class (with cluster id, and embedding ids for all embeddings in cluster)
# if necessary later. For now, it's not useful.

class Clusterer:
    def __init__(self, embeddings: np.ndarray, seed: int=43):
        """
        Notes
        -----
        The embeddings matrix should be ordered.
        """
 
        self.embeddings = embeddings
        self.seed = seed


    def get_clusters(self, num_clusters: int=5) -> list[int]:
        """
        Returns a set of pointer idx mapping each embedding vector to its corresponding cluster

        Returns
        -------
        embedding_idx_to_cluster_id : list[int]
            List mapping each embedding to its corresponding cluster.
        """
        # get indices mapping each embedding to its corresponding cluster
        embedding_idx_to_cluster_id =  KMeans(
                                            n_clusters=num_clusters,
                                            random_state=self.seed
                                        ).fit_predict(self.embeddings)
        return embedding_idx_to_cluster_id

    def compute_centroid(self):
        raise NotImplementedError
       
