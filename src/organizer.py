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

Facade class; a receptionist.
"""

from .parser import KeepParser
from .models import Note, Chunk
from .embedder import Embedder  
from .search import SemanticSearcher, SearchResult
from .clusterer import Clusterer
from . import chunking
from .graph import SemanticGraphBuilder


import numpy as np
from pathlib import Path
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer

from functools import wraps

@dataclass
class QueryResult:
    score: float
    note: Note
    chunk: Chunk

@dataclass
class ClusterResult:
    cluster_id: int
    embeddings: np.ndarray
    notes: list[Note]
    chunks: list[Chunk]
    representative_text: str
    radius: float
    density: float

class ModelNotLoadedError(RuntimeError):
    """ Raised when a method is called before notes are loaded in model with `from_keep_directory` or similar """
    pass

class BrainOrganizer:
    def __init__(self, notes_dir: str | Path, model_name: str):
        # sentence transformer model
        self.model_name = model_name
        self.notes_dir = notes_dir

        # helper instances
        self.parser = KeepParser(notes_dir)
        self.embedder = Embedder(SentenceTransformer(model_name, device='cuda', local_files_only=True))
        self.searcher: SemanticSearcher | None = None
        self.clusterer: Clusterer | None = None
        self.grapher: SemanticGraphBuilder | None = None

        # notes, embeddings, chunks (unpopulated until and `embed_from` method is called).
        # embeddings and chunks stored such that self.embeddings[i, :] corresponds to chunks[i], always.
        self.notes: list[Note] = []
        self.embeddings: np.ndarray | None = None
        self.chunks: list[Chunk] = []

    def requires_loading(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.embeddings is None:
                raise ModelNotLoadedError(
                        f"{self.__class__.__name__} must be loaded before "
                        f"{method.__name__} is called. Call `from_keep_directory()` or similar first."
                    )
            return method(self, *args, **kwargs)
        return wrapper
  
    # load brain (parse and embed) from Keep notes
    @classmethod
    def from_keep_directory(cls, 
                            keep_dir: str | Path,
                            model_name: str="sentence-transformers/all-MiniLM-L6-v2",
                            metric: str='cosine',
                            ) -> "BrainOrganizer":
        brain = cls(keep_dir, model_name)

        # parse keep notes into a list of Note (domain objects)
        brain.parser.get_keepjson_files()
        notes: list[Note] = brain.parser.create_notes()
        brain.notes = notes

        # chunk Note objects into list of Chunk (objects with content ready to be passed to embedder)
        # currently chunking notes into paragraphs via smart chunking without context
        # TODO: pass these as arguments so the user can select which chunking algorithm
        chunks: list[Chunk] = chunking.chunk_notes(
                notes,
                chunking.chunk_by_paragraphs_smart,
                include_context=False, 
                soft_min_len=300, max_len=1500
                )
        brain.chunks = chunks

        embeddings = brain.embedder.embed_many([chunk.text for chunk in chunks])
        brain.embeddings = embeddings

        # create searcher
        brain.searcher = SemanticSearcher(brain.embeddings, metric=metric)

        # create clusterer
        brain.clusterer = Clusterer(brain.embeddings)

        # create grapher
        brain.grapher = SemanticGraphBuilder(brain.embeddings, metric=metric)

        return brain

    # tool methods
    @requires_loading
    def search_notes(self, query: str) -> list[QueryResult]:
        # search notes for best match to query. list of all embeddings in order of closeness returned
        embedded_query = self.embedder.embed(query)
        search_results: list[SearchResults] = self.searcher.search(embedded_query)
      
        # package results into a QueryResult
        query_results = []
        for sr in search_results:
            chunk = self.chunks[sr.embedding_idx]
            note = self.notes[chunk.note_id]
            score = sr.score
            query_results += [QueryResult(score, note, chunk)] 
        return query_results

    @requires_loading
    def cluster_notes(self, num_clusters: int=5) -> list[ClusterResult]:
        # cluster embeddings into `num_clusters` clusters and take stats
        embedding_idx_to_cluster_id = self.clusterer.fit_clusters(num_clusters)
        rep_idxs = self.clusterer.get_representative_embeddings()
        radii = self.clusterer.compute_radius()
        densities = self.clusterer.compute_density()

        # package results and analysis into a ClusterResult
        clusters = []
        for current_cluster in range(num_clusters):
            mask = embedding_idx_to_cluster_id == current_cluster
            embeddings = self.embeddings[mask]
            chunks = np.array(self.chunks)[mask]
            notes = [self.notes[chunk.note_id] for chunk in chunks]
            representative_text = self.notes[self.chunks[rep_idxs[current_cluster]].note_id].title
            radius, density = radii[current_cluster], densities[current_cluster]
            clusters += [ClusterResult(
                                    current_cluster,
                                    embeddings, notes, chunks,
                                    representative_text,
                                    radius,
                                    density
                                )]
        return clusters 

    # TODO: feed_to_LLM
    def feed_to_LLM(self):
        """ 
        Use an LLM to come up with topic summaries to label clusters
        among other things
        """
        raise NotImplementedError

    @requires_loading
    def create_graph(self, graph_type: str='mutual-knn', **kwargs):
        """ Returns the graph object and adjusts internal state of brain.grapher """
        graph_types = {
                'mutual-knn' : self.grapher.create_mutual_knn_graph,
                'hairball'   : self.grapher.create_hairball_graph,
                'knn'        : self.grapher.create_knn_graph,
                'threshold'  : self.grapher.create_threshold_graph
                }
        
        graph_builder = graph_types.get(graph_type)
        if graph_builder is None:
            raise ValueError(f"Unkown graph type: {graph_type!r}")
        graph = graph_builder(**kwargs)
        
        # TODO: do analysis on graph 

        # add attr metadata to nodes
        for embedding_id in graph.nodes:
            chunk = self.chunks[embedding_id]

            graph.nodes[embedding_id].update({
                "chunk_text" : chunk.text,
                "note_id" : chunk.note_id,
                "note_text" : self.notes[chunk.note_id].text, # NOTE: this will likely be deprecated since it repeatedly copies the same note text for multiple nodes
                "chunk_length": len(chunk.text),
                "note_length": len(self.notes[chunk.note_id].text)
            })
        return graph
    
    @requires_loading
    def get_notes(self) -> list[Note]:
        return self.notes

    @requires_loading
    def get_chunks(self) -> list[Chunk]:
        return self.chunks
