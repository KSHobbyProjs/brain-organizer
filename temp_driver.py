from src.parser import KeepParser
from src.embedder import Embedder
from src.search import SemanticSearcher

from sentence_transformers import SentenceTransformer

parser = KeepParser("tests/Takeout/Keep")

files = parser.get_keepjson_files()
notes = parser.create_notes()

print(f"Loaded {len(notes)} notes.")
print()
print(notes[0])
print()

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cuda")
embedder = Embedder(model)
embeddings = embedder.embed_many([note.to_text() for note in notes])

print(f"Loaded embeddings. Shape {embeddings.shape}.")
print()
#print(embeddings[0])
print()

searcher = SemanticSearcher(embeddings, notes)
query = "introspection and fixing myself"
embedded_query = embedder.embed(query)
search_results = searcher.search(embedded_query, k=5)

top_result_note = search_results[0].note

for i, result in enumerate(search_results):
    print(f"Semantic search result number {i} score: {result.score}, index: {result.index}\n")
print("------- TOP RESULT ---------------\n")
print(f"Title: {top_result_note.title}\n\n")
print(f"Body: {top_result_note.text}")
