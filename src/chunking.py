# a module to chunk notes in different ways
from .models import Note, Chunk
from collections.abc import Callable

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
 
def chunk_fullnote(note: Note) -> list[str]:
    return [note.text]

def chunk_paragraphs(note: Note) -> list[str]:
    return note.text.strip().split("\n\n")

def chunk_paragraphs_smart(note: Note, min_len: int=200, max_len: int=1000) -> list[str]:
    # TODO: Bug if there is an extremely lengthy sentence.
    # TODO: convert the problem to tokens instead of raw text length.
    """
    Chunk note contents into paragraphs, but shrink or extend paragraphs
    that are too long or too short. 

    For instance, a paragraph with length between min_len and max_len will
    pass as a chunk. If a paragraph is less than min_len, it will be added 
    to paragraphs after (preserving paragraph structure) until it's length 
    is between min_len and max_len. If a paragraph is larger than max_len,
    then it will be divided into chunks of approximately max_len (preserving
    sentence structure as best as possible).

    Parameters
    ----------
    note : Note
        A note object including the notes text and metadata.
    min_len : int, optional
        Minimum length of each chunk. Default = 200.
    max_len : int, optional
        Maximum length of each chunk. Default = 1000.

    Returns
    -------
    chunks : list[str]
        A list of the chunks making up the note.
    """

    def _split_paragraph(paragraph: str) -> list[str]:
        """ 
        Split a paragraph into bits if it's above a certain threshold.
        Separates a string into chunks with sizes no larger than max_len
        such that sentence structure is maintained.

        BUG: A sentence like `Dr. Smith studied` is not parsed properly due
        to the splitting at '. '
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
            if len(candidate) > max_len and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
            else:
                current_chunk = candidate
            
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    note_text = note.text.strip()

    chunks: list[str] = []
    current_chunk = ""         # current chunk str
    remaining_text = note_text # remaining text in note
    while remaining_text:
        # split off next paragraph from remaining text
        split = remaining_text.split("\n\n", 1) 
      
        if len(split) == 2:
            next_paragraph, remaining_text = split
        else:
            next_paragraph = split[0]  # if that was the last paragraph, process it and exit
            remaining_text = ""

        # if current chunk becomes larger than max_len after adding next paragraph
        if len(current_chunk + next_paragraph) > max_len: 
            if current_chunk:                       # make sure the current chunk isn't "", then add current chunk w/o next paragraph to chunks
                chunks.append(current_chunk.strip())
            if len(next_paragraph) < min_len:       # if next paragraph is smaller than min_len, reset current chunk to this paragraph to add more to it
                current_chunk = next_paragraph
            else:
                chunks.extend(_split_paragraph(next_paragraph)) # if next paragraph is larger than min_len, process it (split if necessary; otherwise add to chunks), and reset current chunk
                current_chunk = ""
        # if not larger than max_len but larger than min_len after adding next paragraph to chunk, add the current chunk + next paragraph to chunks and reset current chunk
        elif len(current_chunk + next_paragraph) >= min_len:
            chunks.append((current_chunk + "\n\n" + next_paragraph).strip())
            current_chunk = ""
        # if current chunk + next paragraph is still smaller than min_len, then update current chunk and continue
        else:
            current_chunk += ("\n\n" + next_paragraph)

    # add current chunk remaining after while loop breaks to chunks
    if current_chunk:
        chunks.append(current_chunk.strip())

    for chunk in chunks:
        assert len(chunk) <= max_len, len(chunk)
    return chunks

def chunk_by_token_number(note: Note, num_tokens: int=50) -> list[str]:
    note_text = note.text.strip()
    return [note_text[j:j+num_tokens] for j in range(0, len(note_text), num_tokens)]

def chunk_by_AI_summary():
    raise NotImplementedError
