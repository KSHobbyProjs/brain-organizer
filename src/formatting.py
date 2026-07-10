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
            f"{result.chunk.text[:CUTOFF]}",
            Rule(),
        ])

    return Group(*renderables)

def format_cluster_results(cluster_results: list[ClusterResult]) -> Group:
    renderables = [f"[blue]Clusters[/blue]", Rule()]
    for cluster in cluster_results:
        renderables.extend([f"[bold cyan]Cluster # {cluster.cluster_id}[/bold cyan]"])
        renderables.extend([c.text for c in cluster.chunks[:CHUNKS_PER_CLUSTER]])
        renderables.extend([Rule()])
    
    return Group(*renderables)
        


