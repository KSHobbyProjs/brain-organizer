from src.parser import KeepParser
from src.embeddings import Embedder

from sentence_transformers import SentenceTransformer

parser = KeepParser("tests/Takeout/Keep")

files = parser.get_keepjson_files()
notes = parser.create_notes()

print(f"Loaded {len(notes)} notes.")
print()
print(notes[0])
print()

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embedder = Embedder(model)
embeddings = embedder.embed_many([note.to_text() for note in notes])

print(f"Loaded embeddings. Shape {embeddings.shape}.")
print()
print(embeddings[0])
