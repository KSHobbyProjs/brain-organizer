# formatting.py
# A helper module storing different formatting functions for the CLI

from .organizer import QueryResult, ClusterResult

from rich.console import Group
from rich.rule import Rule

CUTOFF = 500
CHUNKS_PER_CLUSTER = 3

def format_query_results(query_results: list[QueryResult]) -> Group: 
    renderables = []
    for i, result in enumerate(query_results):
        renderables.extend([
            f"[bold cyan]Result # {i+1}[/bold cyan]",
            f"[blue]Score: {result.score}[/blue]",
            f"[white]{result.chunk.text[:CUTOFF]}[/white]",
            Rule(),
        ])

    return Group(*renderables)

def format_cluster_results(cluster_results: list[ClusterResult]) -> Group:
    renderables = [f"[blue]Clusters[/blue]", Rule()]
    for cluster in cluster_results:
        renderables.extend([(
                f"[bold cyan]Cluster # {cluster.cluster_id+1} ({len(cluster.chunks)} chunks, "
                f"Topic: {cluster.representative_text}, Radius: {cluster.radius}, Density: {cluster.density})"
            )])
        renderables.extend([f"[white]{c.text}[/white]\n" for c in cluster.chunks[:CHUNKS_PER_CLUSTER]])
        renderables.extend([Rule()])
    
    return Group(*renderables)
        
def format_open_note(query_result: QueryResult) -> str:
    note_content = query_result.note.to_full_note()
    chunk_text = query_result.chunk.text

    start_idx = note_content.find(chunk_text)
    end_idx = start_idx + len(chunk_text)

    full_note = (
            f"[blue]Score: {query_result.score}[/blue]\n"
            f"{note_content[:start_idx]}"
            f"[red]{chunk_text}[/red]"
            f"{note_content[end_idx:]}"
        )
    return full_note

def format_open_cluster_note(cluster_result: ClusterResult, chunk_idx: int) -> str:
    chunk_text = cluster_result.chunks[chunk_idx].text
    note_content = cluster_result.notes[chunk_idx].to_full_note()

    start_idx = note_content.find(chunk_text)
    end_idx = start_idx + len(chunk_text)

    full_note = (
            f"[blue]Note {chunk_idx+1} in Cluster {cluster_result.cluster_id+1}[/blue]\n"
            f"{note_content[:start_idx]}"
            f"[red]{chunk_text}[/red]"
            f"{note_content[end_idx:]}"
        )
    return full_note
 

