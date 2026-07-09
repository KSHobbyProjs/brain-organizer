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

from .parser import KeepParser
from .models import Note, Chunk
from .embedder import Embedder  
from .search import SemanticSearcher, SearchResult
from .clusterer import Clusterer
from . import chunking

import numpy as np
from pathlib import Path
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer

@dataclass
class QueryResult:
    score: float
    note: Note
    chunk: Chunk

@dataclass
class ClusterResult:
    cluster_id: int
    notes: list[Note]
    chunks: list[Chunk]

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

        # notes, embeddings, chunks, and chunks_idx (unpopulated until and `embed_from` method is called)
        # embeddings and chunks stored such that self.embeddings[i, :] corresponds to chunks[i], always.
        self.notes: list[Note] = []
        self.embeddings: np.ndarray | None = None
        self.chunks: list[str] = []
  
    # load brain (parse and embed) from Keep notes
    @classmethod
    def from_keep_directory(cls, 
                            keep_dir: str | Path,
                            model_name: str="sentence-transformers/all-MiniLM-L6-v2"
                            ) -> "BrainOrganizer":
        brain = cls(keep_dir, model_name)

        # parse keep notes into a list of Note (domain objects)
        brain.parser.get_keepjson_files()
        notes: list[Note] = brain.parser.create_notes()
        brain.notes = notes

        # chunk Note objects into list of Chunk (objects with content ready to be passed to embedder)
        # currently chunking notes into paragraphs with added title / label context
        chunks: list[Chunk] = chunking.chunk_paragraphs_with_context(notes)
        brain.chunks = chunks

        embeddings = brain.embedder.embed_many([chunk.text for chunk in chunks])
        brain.embeddings = embeddings

        # create searcher
        brain.searcher = SemanticSearcher(brain.embeddings)

        # create clusterer
        brain.clusterer = Clusterer(brain.embeddings)

        return brain

    # tool methods
    def search_notes(self, query: str, k: int=1) -> list[QueryResult]:
        # search notes for best match to query
        embedded_query = self.embedder.embed(query)
        search_results: list[SearchResults] = self.searcher.search(embedded_query, k=k)
       
        query_results = []
        for sr in search_results:
            chunk = self.chunks[sr.embedding_idx]
            note = self.notes[chunk.note_id]
            score = sr.score
            query_results += [QueryResult(score, note, chunk)] 
        return query_results

    def cluster_notes(self, num_clusters: int=5) -> list[ClusterResult]:
        # cluster embeddings into `num_clusters` clusters
        embedding_idx_to_cluster_id = self.clusterer.cluster(num_clusters)

        clusters = []
        for current_cluster in range(num_clusters):
            chunks = [self.chunks[i] for i, idx in enumerate(embedding_idx_to_cluster_id) if idx == current_cluster]
            notes = [self.notes[chunk.note_id] for chunk in chunks]
            clusters += [ClusterResult(current_cluster, notes, chunks)]
        return clusters 

    def get_notes(self) -> list[Note]:
        return self.notes
