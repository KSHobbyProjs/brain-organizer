# embeddings.py
# A class for embedding a list of Note objects into a vector space using a pre-trained sentence
# transformer model

from typing import Protocol
import numpy as np

class EmbeddingModel(Protocol):
    def encode(self, text: str) -> np.ndarray:
        ...

class Embedder:
    def __init__(self, model: EmbeddingModel):
        self.model = model

    def embed(self, text: str) -> np.ndarray:
        embeddings = self.model.encode(text)
        return embeddings

    def embed_many(self, texts: list[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            embedding = self.model.encode(text)
            embeddings.append(embedding)
        embeddings = np.array(embeddings)
        return embeddings


