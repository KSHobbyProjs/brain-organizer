# a module to chunk notes in different ways
from .models import Note, Chunk
from collections.abc import Callable

import math as m

def chunk_notes(
        notes: list[Note],
        chunk_func: Callable[[Note], list[str]],
        include_context: bool = False,
        *args,
        **kwargs
        ) -> list[Chunk]:
    
    chunks = []
    for note_id, note in enumerate(notes):
        note_chunks = chunk_func(note, *args, **kwargs)
        
        for chunk_text in note_chunks:
            if include_context:
                labels_str = " ".join(note.labels)
                chunk_text = (
                        f"Title: {note.title}\n\n"
                        f"Labels: {labels_str}\n\n"
                        f"{chunk_text}"
                    )
            chunks.append(Chunk(note_id, chunk_text))
    return chunks

# -------------------------------------- Chunking methods ----------------------------------------
def chunk_by_fullnote(note: Note) -> list[str]:
    return [note.text]

def chunk_by_paragraphs(note: Note) -> list[str]:
    return note.text.strip().split("\n\n")

def chunk_by_token_number(note: Note, num_tokens: int=50) -> list[str]:
    note_text = note.text.strip()
    return [note_text[j:j+num_tokens] for j in range(0, len(note_text), num_tokens)]

def chunk_by_AI_summary():
    raise NotImplementedError

def chunk_by_paragraphs_smart(note: Note, soft_min_len: int=300, max_len: int=1500) -> list[str]:
    """ 
    Chunk note text into sections while preserving paragraph boundaries.

    The algorithm operates in two stages:
    1. The note text is split into paragraphs, and paragraphs longer than `max_len` are split into smaller pieces.
    2. Adjacent paragraph pieces are combined when possible. Combined paragraph pieces are always kept below `max_len`. 
       The algorithm attempts to keep chunks above `soft_min_len`.

    Parameters
    ----------
    note : Note
        The note containing the note text.
    soft_min_len : int 
        Target minimum section length (not always reached; see Notes).
    max_len : int
        Maximum section length.

    Returns
    -------
    list[str]
        List of sections.

    Note
    ----
    Paragraph order is preserved.
    
    `soft_min_len` is not a strict lower bound. Some chunks may be shorter than this value when merging
    would otherwise violate the `max_len` condition.

        The original implementation circumvented this issue by building chunks line by line, 
        but it was far too messy, and the tradeoff in chunk quality is small.
    """
    # split note text into paragraphs
    paragraphs = note.text.strip().split("\n\n")
    # process paragraphs by splitting them if they're too long
    parsed_paragraphs = [
            pp
            for p in paragraphs 
            for pp in _process_paragraph(p, max_len)
            ]
    # link paragraphs together so each chunk text is between soft_min_len and max_len long (as best as possible)
    packed_paragraphs = _pack_paragraphs(parsed_paragraphs, soft_min_len, max_len)
    return packed_paragraphs

# -------------------------------------- Helper methods ------------------------------------------
def _process_paragraph(paragraph: str, max_len: int) -> list[str]:
    """ Split long paragraphs into sections of length max_len """
    paragraph = paragraph.strip()
    if len(paragraph) <= max_len:
        return [paragraph]
   
    return [
            paragraph[i : i + max_len]
            for i in range(0, len(paragraph), max_len)
        ]

def _pack_paragraphs(paragraphs: list[str], soft_min_len: int, max_len: int) -> list[str]:
    """
    Squeeze together paragraphs in an ordered list so that most elements of the list 
    have a length between min_len and max_len while maintaining the order of the strings.

    Notes
    ----
    This function assumes that no elements of `paragraphs` is longer than max_len on
    its own.

    Because order is to be maintained and no paragraph is allowed to breach max_len, there 
    can possibly be some paragraphs whose length is below soft_min_len.
    """
    packed_paragraphs = []
    paragraphs = paragraphs.copy() # so original paragraphs list isn't destroyed

    # loop backward over paragraphs, adding paragraphs together as necessary
    i = len(paragraphs) - 1
    while i > 0:
        n = len(paragraphs[i])
        if n >= soft_min_len and n <= max_len:
            packed_paragraphs.append(paragraphs[i])
        elif n < soft_min_len:
            candidate = paragraphs[i-1] + "\n\n" + paragraphs[i]
            if len(candidate) > max_len:
                packed_paragraphs.append(paragraphs[i]) # allows a paragraph smaller than soft_min_len to pass through
            else:
                paragraphs[i-1] = candidate
        # no need for n > max_len check because of assumption (see Notes)
        paragraphs.pop()
        i -= 1
    
    # append the remaining paragraph after while loop finishes
    packed_paragraphs.append(paragraphs[0])

    return packed_paragraphs[::-1] # flip order since walked over list backwards

def _sentence_splitter(paragraph: str, max_len: int) -> list[str]:
    """ 
    Split long paragraphs into sections of max_len, while preserving sentence
    structure as best as possible
    
    Note: A sentence like `Dr. Smith studied` is not parsed properly due to
    the splitting at '. '.
    """
    # if paragraph is smaller than max_len, don't split; return full paragraph
    if len(paragraph.strip()) <= max_len:
        return [paragraph.strip()]

    # split paragraphs into its sentences (approximately)
    sentences = paragraph.strip().split(". ")
   
    current_chunk = ""
    chunks = []
    # add sentences of paragraph together until doing so would make the current sum larger than max_len,
    # then put that sum of sentences into chunks, reset the current chunk, and repeat until the entire
    # paragraph is swept through.
    for sentence in sentences:
        candidate = current_chunk + sentence + ". "
        if len(candidate) > max_len:
            if current_chunk:
                chunks.append(current_chunk.strip())
            else:
                # if current_chunk="", the sentence is longer than max_len, so cut it into pieces
                chunks.extend([sentence[i:i+max_len] for i in range(0, len(sentence), max_len)])
            current_chunk = sentence + ". "
        else:
            current_chunk = candidate
        
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks
