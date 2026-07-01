# clustering.py
# A class for clustering embedded notes

from dataclasses import dataclass
import numpy as np
from sklearn.cluster import KMeans

from .parser import Note

@dataclass
class ClusterResult:
    cluster_notes: dict[int, (list[Note], np.ndarray)]

    def get_ordered_embeddings(self) -> np.ndarray:
        """Collapses dictionary for easier parsing in visualizer.py"""
        # compute idx array mapping each embedding to its cluster; shape (num_embeddings,)
        idx = np.concatenate([
                        [cluster_num]*len(cluster_embedding[1]) 
                        for cluster_num, cluster_embedding
                        in self.cluster_notes.items() 
                    ])         
        # collapse embeddings along first axis
        cluster_embeddings = np.concatenate([embedding[1] for embedding in self.cluster_notes.values()]) # concatenate embedding matrix
        return idx, cluster_embeddings    
            

    def to_preview(self) -> str:
        """ Create a preview of the cluster including the first 3 notes for each cluster """
        preview = ""
        # grab contents from each cluster
        for cluster_num, cluster_contents in self.cluster_notes.items():
            preview += f"Cluster {cluster_num+1}\n\n" # title the cluster
            # display contents of first three notes
            notes, _ = cluster_contents
            for note in notes[:3]:
                preview += f"{note.to_preview()}\n\n"
            preview += "-"*250 + "\n\n" # end with a rule to separate sectors
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

    def cluster(self, num_clusters: int=5) -> ClusterResult:
        # get indices mapping each embedding to its corresponding cluster
        kmeans_labels = KMeans(n_clusters=num_clusters, random_state=42).fit_predict(self.embeddings)

        cluster_notes: dict[int, (list[Note], np.ndarray)] = {}
        for i in range(num_clusters):
            # get indices for each embedding in cluster i
            idx = [j for j, label in enumerate(kmeans_labels) if label == i]

            # get notes and embeddings for cluster i
            notes = [self.notes[j] for j in idx]
            embeddings = self.embeddings[idx, :]

            # populate dictionary at cluster i
            cluster_notes[i] = (notes, embeddings)

        clusters = ClusterResult(cluster_notes)
        return clusters
