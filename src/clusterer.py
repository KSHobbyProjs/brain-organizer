# clustering.py
# A class for clustering embedded notes

import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

from functools import wraps

class NoClustersError(RuntimeError):
    """ Raised when a method requiring clusters is called before getting clusters. """
    pass

class Clusterer:
    def __init__(self, embeddings: np.ndarray, seed: int=43):
        """
        Notes
        -----
        The embeddings matrix should be ordered.
        """
 
        self.embeddings = embeddings
        self.seed = seed

        self._embedding_cluster_map: np.ndarray | None = None
        self._num_clusters: int | None = None

        # cache vars
        self._centroids: dict[int, np.ndarray] | None = None
        self._distance_space: np.ndarray | None = None

    def requires_clusters(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if self._embedding_cluster_map is None:
                raise NoClustersError(
                        f"{self.__class__.__name__} must be fitted before "
                        f"{method.__name__} is called. Call `fit_clusters()` first."
                    )
            return method(self, *args, **kwargs)
        return wrapper

    def fit_clusters(self, num_clusters: int=5) -> list[int]:
        """
        Returns a set of pointer idx mapping each embedding vector to its corresponding cluster
        
        Parameters
        ----------
        num_clusters: int
            The number of clusters to fit the data with.

        Returns
        -------
        embedding_cluster_map : list[int]
            List mapping each embedding to its corresponding cluster.
        """
        # get indices mapping each embedding to its corresponding cluster 
        self.kmeans = KMeans(n_clusters=num_clusters, random_state=self.seed)
        embedding_cluster_map = self.kmeans.fit_predict(self.embeddings)

        self._embedding_cluster_map = np.array(embedding_cluster_map)
        self._num_clusters = max(self._embedding_cluster_map) + 1
        self._centroids = None # invalidate cache upon re-fitting
        self._distance_space = None
        return embedding_cluster_map

    @requires_clusters
    def get_centroids(self) -> dict[int, np.ndarray]:
        """
        Get the centroids of each cluster.

        Returns
        ----------
        dict[int, np.ndarray]:
            Dictionary where keys are cluster ids and values are the cetroid embedding.

        Notes
        -----
        This method assumes a `get_clusters` method has already been run.
        """ 
        if self._centroids is None: 
            self._centroids = {
                            i : np.mean(self.embeddings[self._embedding_cluster_map==i], axis=0)
                            for i in range(self._num_clusters)
                        }
        return self._centroids
    
    @requires_clusters
    def to_distance_space(self) -> np.ndarray:
        """
        Computes the distance from each embedding to its respective centroid.

        Returns
        -------
        list[float]
            List of distances. The element at the i-th index corresponds to
            the distance of embeddings[i] to its centroid.
        """
        if self._distance_space is None:
            centroids = self.get_centroids()
            self._distance_space = np.array([
                    np.linalg.norm(embedding - centroids[self._embedding_cluster_map[i]])
                    for i, embedding in enumerate(self.embeddings)
                ])
        return self._distance_space
    
    @requires_clusters
    def get_representative_embeddings(self) -> dict[int, int]:
        """
        Gets the embedding closest to the centroid for each cluster.

        Returns
        -------
        dict[int, int]
            A dictionary where the keys are cluster ids and the values
            are the embedding idx corresponding to the embedding
            closest to the centroid of that cluster.
        """
        distance_space = self.to_distance_space()
       
        representative_embeddings_idx = {}
        for i in range(self._num_clusters):
            # NOTE: I initially did this by copying the array and setting
            #       non-cluster elements to np.inf. But np.where allows
            #       us to avoid copying all together. The reason we can do
            #       this is because boolean indexing never re-orders elements
            # isolate only the distances from a centroid within cluster i
            mask = self._embedding_cluster_map == i
            cluster_idx = np.where(mask)[0]

            # store minimum idx as pointer to representative embedding for cluster i
            representative_embeddings_idx[i] = cluster_idx[np.argmin(distance_space[mask])]
        return representative_embeddings_idx
               
    @requires_clusters
    def compute_radius(self) -> dict[int, float]:
        """
        Computes the radius of each cluster. Radius is defined as the average (euclidean)
        distance of the embeddings from their respective centroid.
        
        Returns
        -------
        dict[int, float]
            A dictionary where the keys are cluster ids and the values are the
            radius for that cluster.
        """
        distance_space = self.to_distance_space()
        return {
                i : np.mean(distance_space[self._embedding_cluster_map==i])
                for i in range(self._num_clusters)
            }

    @requires_clusters
    def compute_density(self, metric: str='euclidean', k: int=5) -> dict[int, float]:
        """
        Computes the density of each cluster. Density is defined as the average distance
        between each embedding and its k closest neighbors in its cluster.

        Parameters
        ----------
        metric : str, optional
            The metric by which to score embedding closeness. Default is cosine similarity.
        k : int, optional
            The number of nearest neighbors to consider for the density. Default is 5.

        Returns
        -------
        dict[int, float]
            The average density in each cluster. Keys are cluster ids, values are average density
            in that cluster.

        Note
        ----
        This method can fail if `k` is larger than the number of embeddings in any given cluster.
        """
        # quickly sweep through each cluster to validate that k < len(cluster) for all clusters
        # validate first so we fail fast before perfoming the more expensive nn loop.
        for cluster in range(self._num_clusters):
            cluster_size = np.sum(self._embedding_cluster_map == cluster)
            if k > cluster_size:
                raise ValueError(
                                f"k={k} is larger than the length of cluster {cluster}. "
                                f"Decrease k and try again."
                            )

        nn = NearestNeighbors(n_neighbors=k, metric=metric)
        return {
                i : np.mean(
                        nn.fit(
                            self.embeddings[self._embedding_cluster_map==i]
                        ).kneighbors()[0]
                    )
                for i in range(self._num_clusters)
            }
