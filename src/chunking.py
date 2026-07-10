# a module to chunk notes in different ways
from .models import Note, Chunk

# TODO: possibly make it so that this module is dedicated strictly to parsing one Note into Chunks rather than
# taking an arbitrary list

def chunk_fullnote(notes: list[Note]) -> list[Chunk]:
    chunks = []
    for i, note in enumerate(notes):
        labels_str = " ".join(note.labels)
        chunk_txt = f"Title: {note.title}\n\nLabels: {labels_str}\n\n{note.text}"
        chunks += [Chunk(i, chunk_txt)]

def chunk_paragraphs(notes: list[Note]) -> list[Chunk]:
    chunks = []
    for i, note in enumerate(notes):
        note_paragraphs = note.text.strip().split("\n\n")
        for paragraph in note_paragraphs:
            chunks += [Chunk(i, paragraph)]
    return chunks

def chunk_paragraphs_with_context(notes: list[Note]) -> list[Chunk]:
    chunks = []
    for i, note in enumerate(notes):
        labels_str = " ".join(note.labels)
        context_str = f"Title: {note.title}\n\nLabels: {labels_str}\n\n"
        note_paragraphs = note.text.strip().split("\n\n")
        for paragraph in note_paragraphs:
            chunk_txt = context_str + paragraph
            chunks += [Chunk(i, chunk_txt)]
    return chunks

def chunk_by_token_number(notes: list[Note], num_tokens: int=50) -> list[Chunk]:
    chunks = []
    for i, note in enumerate(notes):
        note_txt = note.text.strip()
        chunks_txt = [note_txt[j:j+num_tokens] for j in range(0, len(note_txt), num_tokens)]
        for chunk_txt in chunks_txt:
            chunks += [Chunk(i, chunk_txt)]
    return chunks

def chunk_by_AI_summary():
    raise NotImplementedError
