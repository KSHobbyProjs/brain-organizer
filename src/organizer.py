# organizer.py
# A module to coordinate the pieces of the project:
# (1) parse and load notes
# (2) embed notes
# (3) search notes with query
# (4) TODO: cluster notes
# (5) TODO: timeline

from .parser import KeepParser, Note
from .embedder import Embedder  
from .search import SemanticSearcher

import numpy as np
from pathlib import Path

class BrainOrganizer:
    def __init__(self, notes_dir: str | Path, model_name: str):
        # sentence transformer model
        self.model = model
        self.notes_dir = notes_dir

        # helper instances
        self.parser = KeepParser(notes_dir)
        self.embedder = Embedder(SentenceTransformers(model, device='cuda'))
        self.searcher: SemanticSearcher | None = None

        # notes and embeddings (unpopulated until and `embed_from` method is called)
        self.notes: list[Note] = []
        self.embeddings: np.ndarray | None = None
  
    # load brain (parse and embed) from Keep notes
    def from_keep_directory(cls, 
                            keep_dir: str | Path,
                            model_name: str="sentence-transformers/all-MiniLM-L6-v2"
                            ) -> "BrainOrganizer":
        brain = cls(keep_dir, model_name)

        # parse keep notes 
        self.parser.get_keepjson_files()
        notes = self.parser.create_notes()
        self.notes = notes

        # embed keep notes using sentence transformer model
        embeddings = self.embedder.embed_many([note.to_text() for note in notes])
        self.embeddings = embeddings

        # create searcher
        self.searcher = SemanticSearcher(self.embeddings, self.notes)

        # create clusterer
        # TODO 

        # create timeline creator
        # TODO
        return brain

    # tool methods
    def search_notes(self, query: str, k: int=1):
        # search notes for best match to query
        embedded_query = self.embedder.embed(query)
        search_results = self.searcher.search(embedded_query, k=k)
        return search_results

    def cluster_notes(self):
        raise NotImplementedError

    def timeline(self):
        raise NotImplementedError
