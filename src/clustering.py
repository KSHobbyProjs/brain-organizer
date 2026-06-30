# clustering.py
# A class for clustering embedded notes

from dataclasses import dataclass
import numpy as np
from sklearn.cluster import KMeans

from .parser import Note

@dataclass
class ClusterResult:
    notes: list[Note]

    def to_preview(self) -> str:
        """ Create a preview of the cluster including the first 3 notes """
        preview = ""
        for note in self.notes[:3]:
            preview += f"{note.to_preview()}\n\n"
        return preview

class Clusterer:
    def __init__(self, embeddings: np.ndarray, notes: list[Note]):
        """
        Notes
        -----
        The embeddings matrix should be ordered. I.e., structured so
        that the ith row corresponds to the embedding vector for note notes[i]
        """
 
        self.embeddings = embeddings
        self.notes = notes

    def cluster(self, num_clusters: int=5) -> dict[int, ClusterResult]:
        kmeans_labels = KMeans(n_clusters=num_clusters, random_state=42).fit_predict(self.embeddings)

        clusters: dict[int, ClusterResults] = {}
        for i in range(num_clusters):
            idx = [j for j, label in enumerate(kmeans_labels) if label == i]
            clusters[i] = ClusterResult([self.notes[j] for j in idx])
        return clusters
