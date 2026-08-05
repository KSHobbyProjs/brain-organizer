# dto module for converting backend objects to frontfacing objects

from dataclasses import dataclass
# only for type hints
from .organizer import QueryResult, ClusterResult
from .models import Chunk, Note


@dataclass
class ChunkData: 
    span: tuple[int, int]
    score: float = None   # score only recorded for query

@dataclass
class Response:
    note: dict
    chunks: list[ChunkData]

@dataclass
class ClusterResponse:
    clusterID: int
    repNote: dict
    repText: str
    radius: float
    density: float
    contents: list[Response]
    numNotes: int
    numChunks: int

def query_results_to_response(query_results: list[QueryResult]):
    responses = {}
    for result in query_results:
        idx = result.chunk.note_id
        if responses.get(idx, None) is None:
            responses[idx] = Response(
                    note=result.note.to_dict(),
                    chunks=[]
                )
        responses[idx].chunks.append( ChunkData(
                            span=result.chunk.span,
                            score=float(result.score)
                    ) )

    # sort chunks so that the best match is at the top
    for r in responses.values():
        r.chunks.sort(
                key=lambda chunk: chunk.score,
                reverse=True
            )
    return list(responses.values())
                
def cluster_results_to_response(cluster_results: list[ClusterResponse]):
    responses = {}
    for i, result in enumerate(cluster_results):
        contents = _get_unique_notes(result.chunks, result.notes)
        responses[i] = ClusterResponse(
                clusterID=result.cluster_id,
                repNote=result.representative_note.to_dict(),
                repText=result.representative_text,
                radius=float(result.radius),
                density=float(result.density),
                contents=contents,
                numNotes=len(contents),
                numChunks=len(result.chunks)
            )
    return list(responses.values())

def _get_unique_notes(chunks: list[Chunk], notes: list[Note]) -> list[Response]:
    """
    Produces a list of Response given a list of chunks and notes.
    Assumes that chunks[idx] corresponds to notes[idx]
    """
    responses = {}
    for chunk, note in zip(chunks, notes):
        idx = chunk.note_id
        if responses.get(idx) is None:
            responses[idx] = Response(
                    note=note.to_dict(),
                    chunks=[]
                )
        responses[idx].chunks.append( ChunkData(
                span=chunk.span
            ) )
    return list(responses.values())
