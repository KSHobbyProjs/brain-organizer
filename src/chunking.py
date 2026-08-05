# a module to chunk notes in different ways
from .models import Note, Chunk
from collections.abc import Callable
from dataclasses import dataclass

import math as m

@dataclass
class TextSpan():
    text: str
    start: int
    end: int

def chunk_notes(
        notes: list[Note],
        chunk_func: str,
        include_context: bool = False,
        *args,
        **kwargs
        ) -> list[Chunk]:

    try:
        chunk_func = CHUNK_METHODS[chunk_func]
    except KeyError:
        raise ValueError(f"Unknown chunking method: '{chunk_func}'")
    
    chunks = []
    for note_id, note in enumerate(notes):
        chunks_spans = chunk_func(note, *args, **kwargs)
 
        for chunk_span in chunks_spans:
            chunk_text = chunk_span.text.strip()
            span = (chunk_span.start, chunk_span.end)
            if include_context:
                labels_str = " ".join(note.labels)
                chunk_text = (
                        f"Title: {note.title}\n\n"
                        f"Labels: {labels_str}\n\n"
                        f"{chunk_text}"
                    )
            chunks.append(Chunk(note_id, chunk_text, span))
    return chunks

# -------------------------------------- Chunking methods ----------------------------------------
def chunk_by_fullnote(note: Note) -> list[TextSpan]:
    return [TextSpan(note.text, start=0, end=len(note.text))]

def chunk_by_paragraphs(note: Note) -> list[TextSpan]:
    textspans = []
    start = 0

    for chunk in note.text.split("\n\n"):
        end = start + len(chunk) 
        textspans.append( TextSpan(chunk, start, end) )
        start = end + 2 # TODO: this is hardcoded; better to use regex

    return textspans

# this is poorly named: it's chunking by character #, not token #, but it'll take too long to make the change
def chunk_by_token_number(note: Note, num_tokens: int=50) -> list[TextSpan]:
    textspans = []
    start = 0

    for j in range(0, len(note.text), num_tokens):
        chunk = note.text[j:j+num_tokens]

        end = start + len(chunk)
        textspans.append( TextSpan(chunk, start, end) )
        start = end

    return textspans

def chunk_by_AI_summary():
    raise NotImplementedError

def chunk_by_paragraphs_smart(note: Note, soft_min_len: int=300, max_len: int=1500) -> list[TextSpan]:
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
    paragraphs = note.text.split("\n\n")
    start = 0
    textspans = []
    for paragraph in paragraphs:
        end = start + len(paragraph)
        textspans.append( TextSpan(paragraph, start, end) )
        start = end + 2

    # process paragraphs by splitting them if they're too long
    parsed_paragraphs = [
            pp
            for p in textspans
            for pp in _process_paragraph(p, max_len)
            ]
    # link paragraphs together so each chunk text is between soft_min_len and max_len long (as best as possible)
    packed_paragraphs = _pack_paragraphs(parsed_paragraphs, soft_min_len, max_len)

    return packed_paragraphs

# -------------------------------------- Helper methods ------------------------------------------
def _process_paragraph(paragraph: TextSpan, max_len: int) -> list[TextSpan]:
    """ Split long paragraphs into sections of length max_len """
    if len(paragraph.text) <= max_len:
        return [paragraph]
   
    return [
            TextSpan(
                paragraph.text[i : i + max_len],
                paragraph.start + i,
                paragraph.start + min(i+max_len, len(paragraph.text))
            )
            for i in range(0, len(paragraph.text), max_len)
        ]

def _pack_paragraphs(paragraphs: list[TextSpan], soft_min_len: int, max_len: int) -> list[TextSpan]:
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
        n = len(paragraphs[i].text)
        if n >= soft_min_len and n <= max_len:
            packed_paragraphs.append(paragraphs[i])
        elif n < soft_min_len:
            candidate = paragraphs[i-1].text + "\n\n" + paragraphs[i].text
            if len(candidate) > max_len:
                packed_paragraphs.append(paragraphs[i]) # NOTE: allows a paragraph smaller than soft_min_len to pass through
            else:
                paragraphs[i-1] = TextSpan(
                        candidate,
                        paragraphs[i-1].start,
                        paragraphs[i].end # don't add 2 because candidate is embedded txt not source text
                    )
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

    This is currently unused.
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


CHUNK_METHODS = {
        "smart_paragraphs" : chunk_by_paragraphs_smart,
        "fullnote" : chunk_by_fullnote,
        "paragraphs": chunk_by_paragraphs,
        "token_number": chunk_by_token_number,
        "llm": chunk_by_AI_summary,
    }


