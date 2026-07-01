# organizer.py
"""
A module to coordinate the pieces of the project:
 (1) Loading notes from sources like Keep and parsing them into a domain object (Note)
 (2) Embedding Notes
 (3) Semantic Searching 
 (4) Clustering

Semantic searching and clustering both rely on having all the Notes and embeddings of those notes, 
so this class wraps all this together, allowing a user to instantiate a model by loading / embeddings
notes from a source (e.g., Google Keep) and calling searching and clustering algorithms on this data
without repeatedly having to load notes or recompute embeddings
"""

from .parser import KeepParser, Note
from .embedder import Embedder  
from .search import SemanticSearcher, SearchResult
from .clustering import Clusterer, ClusterResult

import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

class BrainOrganizer:
    def __init__(self, notes_dir: str | Path, model_name: str):
        # sentence transformer model
        self.model_name = model_name
        self.notes_dir = notes_dir

        # helper instances
        self.parser = KeepParser(notes_dir)
        self.embedder = Embedder(SentenceTransformer(model_name, device='cuda'))
        self.searcher: SemanticSearcher | None = None
        self.clusterer: Clusterer | None = None

        # notes and embeddings (unpopulated until and `embed_from` method is called)
        self.notes: list[Note] = []
        self.embeddings: np.ndarray | None = None
  
    # load brain (parse and embed) from Keep notes
    @classmethod
    def from_keep_directory(cls, 
                            keep_dir: str | Path,
                            model_name: str="sentence-transformers/all-MiniLM-L6-v2"
                            ) -> "BrainOrganizer":
        brain = cls(keep_dir, model_name)

        # parse keep notes 
        brain.parser.get_keepjson_files()
        notes = brain.parser.create_notes()
        brain.notes = notes

        # embed keep notes using sentence transformer model
        embeddings = brain.embedder.embed_many([note.to_text() for note in notes])
        brain.embeddings = embeddings

        # create searcher
        brain.searcher = SemanticSearcher(brain.embeddings, brain.notes)

        # create clusterer
        brain.clusterer = Clusterer(brain.embeddings, brain.notes)

        return brain

    # tool methods
    def search_notes(self, query: str, k: int=1) -> list[SearchResult]:
        # search notes for best match to query
        embedded_query = self.embedder.embed(query)
        search_results = self.searcher.search(embedded_query, k=k)
        return search_results

    def cluster_notes(self, num_clusters: int=5) -> ClusterResult:
        # cluster embeddings into `num_clusters` clusters
        clusters = self.clusterer.cluster(num_clusters)
        return clusters 
