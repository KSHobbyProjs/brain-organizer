# organizer.py
# A module to coordinate the pieces of the project:
# (1) parse and load notes
# (2) embed notes
# (3) search notes with query
# (4) TODO: cluster notes
# (5) TODO: timeline

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

        # create timeline creator
        # TODO
        return brain

    # tool methods
    def search_notes(self, query: str, k: int=1) -> list[SearchResult]:
        # search notes for best match to query
        embedded_query = self.embedder.embed(query)
        search_results = self.searcher.search(embedded_query, k=k)
        return search_results

    def cluster_notes(self, num_clusters: int=5) -> dict[int, ClusterResult]:
        # cluster embeddings into `num_clusters` clusters
        clusters = self.clusterer.cluster(num_clusters)
        return clusters
        
    def timeline(self):
        raise NotImplementedError
