#!/usr/bin/env python3
# main.py
# CLI for application

import argparse
import rich.console
from enum import Enum
from functools import wraps

from src.organizer import BrainOrganizer, QueryResult, ClusterResult
import src.visualizer as visualizer
import src.formatting as formatting

# only used for type hints
from src.models import Note, Chunk
from src.search import SearchResult
import networkx as nx

# constants set for display
CUTOFF = 1000

class CmdResult(Enum):
    NONE = 0      # continue with current iteration
    CONTINUE = 2  # move to next iteration
    EXIT = 1      # break out of repl

class BrainCLI:
    def __init__(self, brain: BrainOrganizer, top_k: int=5):
        self.brain = brain
        
        # number of query results to output to terminal at a time
        self.top_k = top_k

        self.console = rich.console.Console()

        self._current_query_results: list[QueryResult] | None = None
        self._current_cluster_results: list[ClusterResult] | None = None
        self._visualizer_on: bool = False
    
        # TODO: add command that allows one to change chunking, metric, and query k
        # TODO: add command that allows one to analyze a specific cluster 
        self.commands = {
                "cluster" : self.do_cluster,
                "plot-clusters": self.do_plot_clusters,
                "open-cluster-note": self.do_open_cluster_note,
                "graph" : self.do_graph,
                "graph-community" : self.do_get_communities,
                "visualize-graph" : self.do_visualize_graph,
                "timeline": self.do_timeline,
                "open" : self.do_open,

                "clear" : self.do_clear,
                "cls" : self.do_clear,
                "change-k": self.do_change_top_k,
                "help" : self.do_help,

                "exit" : self.do_exit,
                "q" : self.do_exit,
                "quit" : self.do_exit
                }
        
    # ---------------------------------- COMMANDS for REPL -------------------------------
    def do_query(self, query_txt: str) -> CmdResult:
        query_results: list[QueryResult] = self.brain.search_notes(query_txt)
        self.console.print(
                formatting.format_query_results(query_results[:self.top_k])
                )
        
        self._current_query_results = query_results # update cache
        return CmdResult.CONTINUE

    def do_cluster(self, num_clusters: str='5') -> CmdResult:
        num_clusters = int(num_clusters)
        cluster_results: list[ClusterResult] = self.brain.cluster_notes(num_clusters)
        self.console.print(
                formatting.format_cluster_results(cluster_results)
                )
        
        self._current_cluster_results = cluster_results # update cache
        return CmdResult.CONTINUE

    def do_plot_clusters(self, dim: str='2') -> CmdResult:
        dim = int(dim)
        if self._current_cluster_results:
            cluster_results = self._current_cluster_results
        else:
            self.console.print("[yellow]No clusters yet loaded. Load clusters with `:cluster`[/yellow]")
            return CmdResult.CONTINUE

        visualizer.plot_clusters(cluster_results, dim)
        return CmdResult.CONTINUE

    def do_timeline(self):
        notes = self.brain.get_notes()
        visualizer.plot_timeline(notes)
        return CmdResult.CONTINUE

    def needs_graph(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.brain.get_graph():
                self.console.print("[yellow]No graph loaded yet. Load graph with `:graph`[/yellow]")
                return CmdResult.CONTINUE
            else:
                return method(self, *args, **kwargs)
        return wrapper

    def do_graph(self, graph_type: str='mutual-knn', **kwargs):
        # TODO: clean this kwargs parser up a little
        if kwargs.get("k") is not None:
            kwargs["k"] = int(kwargs["k"])
        
        try:
            graph = self.brain.create_graph(graph_type, **kwargs)
        except Exception as e: # TODO: right now, this catches all exceptions and just prints them. possibly improve this later
            self.console.print(f"[red]{e}[/red]")
            return CmdResult.CONTINUE
        
        self.console.print(f"Successfuly created {graph_type!r} graph")
        return CmdResult.CONTINUE
    
    @needs_graph
    def do_get_communities(self, resolution: str='.5'):
        # updates graph with community information
        self.brain.label_louvain_communities(float(resolution))

        # send information to cytoscape so color nodes are colored by community
        if not self._visualizer_on:
            self.do_visualize_graph()
        visualizer.change_cytoscape_coloring_basedon_communities(self.brain.get_graph())
        return CmdResult.CONTINUE
   
   # NOTE: This fails if cytoscape is closed mid program. 
   #       If Cytoscape is closed, self._visaulizer_on will
   #       still be set to true, and any function that calls
   #       the visualizer will raise an error. Maybe this is
   #       a hint to separate the two commands and handle
   #       the visualizer better (py4cytoscape might just belong here)
    @needs_graph
    def do_visualize_graph(self):
        success = visualizer.plot_graph_with_cytoscape(self.brain.get_graph())
        if not success:
            self.console.print("[red]Cytoscape is not currently open[/red]")
            return CmdResult.CONTINUE
    
        self.console.print("Successfuly sent current graph object to Cytoscan")
        self._visualizer_on=True
        return CmdResult.CONTINUE
       
    def do_open(self, query_num: str='1'):
        idx = int(query_num) - 1
        if self._current_query_results:
            try:
                selected_query_result = self._current_query_results[idx]
            except IndexError:
                self.console.print("[yellow]Requested note is out of range.\n[/yellow]")
                return CmdResult.CONTINUE
        else:
            self.console.print("[yellow]No notes loaded. Can't run open[/yellow]")
            return CmdResult.CONTINUE

        self.console.print(
                formatting.format_open_note(selected_query_result)
                )
        return CmdResult.CONTINUE

    def do_open_cluster_note(self, cluster_num: str='1', chunk_num: str='1'):
        if not self._current_cluster_results:
            self.console.print("[yellow]No clusters loaded. Cluster notes with `:cluster`[/yellow]")
            return CmdResult.CONTINUE
        
        cluster_idx = int(cluster_num) - 1
        chunk_idx = int(chunk_num) - 1
        try:
            selected_cluster = self._current_cluster_results[cluster_idx]
            self.console.print(
                    formatting.format_open_cluster_note(selected_cluster, chunk_idx)
                    )
        except IndexError:
            self.console.print("[yellow]Requested cluster or note is out of range.")
        return CmdResult.CONTINUE
    
    def do_clear(self) -> CmdResult:
        self.console.clear()
        return CmdResult.CONTINUE

    def do_exit(self) -> CmdResult:
        return CmdResult.EXIT

    def do_change_top_k(self, k: str) -> CmdResult:
        self.top_k = int(k)
        return CmdResult.CONTINUE

    def do_help(self) -> CmdResult:
        # TODO: make this help a little more helpful
        self.console.print("The following commands are available")
        for key in self.commands.keys():
            self.console.print(f"\t{key}")

 
    def handle_commands(self, line: str) -> CmdResult:
        # TODO: check function signature so typos don't break CLI
        """ Returns 0, 1, 2 after executing command """
        cmd, *tokens = line[1:].strip().split(" ")
        args, kwargs = self._parse_tokens(tokens)

        func = self.commands.get(cmd)
        if func is None:
            self.console.print(f"[red]{line!r} is not a recognized command[/red]")
            return CmdResult.CONTINUE
        
        result = func(*args, **kwargs)
        return result

    @staticmethod
    def _parse_tokens(tokens: list[str]) -> (list[str], dict[str,str]):
        # TODO: (possibly) use shlex for better parsing
        args = []
        kwargs = {}
        for token in tokens:
            if "=" in token:
                key, val = token.split("=", 1)
                kwargs[key] = val
            else:
                args.append(token)
        return args, kwargs


    # ----------------------------------- REPL ------------------------------------------
    def repl(self) -> None:
        while True:
            try:
                # read a line of input
                line = input(f"brain:query> ")

                # check for command and run command if so
                if line.startswith(":"):
                    result = self.handle_commands(line)
                # otherwise, assume input is a query
                else:
                    result = self.do_query(line)
                
                if result == CmdResult.EXIT:
                    break
                if result == CmdResult.CONTINUE:
                    continue
                
            except EOFError:
                # handles Ctrl+D and Ctrl+Z
                self.console.print("\nEOF received. Exiting...")
                break

def main():
    """
    The REPL is meant to be the primary program. However, one can use the 
    command line interface to quickly print basic results. Note however that
    these results will use the default parameters when choosing --graph.
    """
    # TODO: parse --graph such that one can pass in args
    parser = argparse.ArgumentParser(
            prog='SemanticSearcher',
            description='Searches Keep notes for notes that best match a query semantically',
            )
    parser.add_argument('directory', type=str)
    parser.add_argument('-q', '--query', type=str)
    parser.add_argument('-c', '--cluster', type=int)
    parser.add_argument('-p', '--plot-clusters', type=int)
    parser.add_argument('-k', '--top-k', type=int, default=5)
    parser.add_argument('-m', '--model-name', type=str, default='sentence-transformers/all-MiniLM-L6-v2')
    parser.add_argument('-t', '--timeline', action='store_true')
    parser.add_argument('-g', '--graph', type=str)
    
    args = parser.parse_args()
    brain = BrainOrganizer.from_directory(args.directory, model_name=args.model_name, parser_method='keep')
    brain_cli = BrainCLI(brain, args.top_k)

    # treat the brain as its own interactive model, 
    # but allow a straight query result if prompted with '--query'
    # the default mode of the repl is to accept queries and spit out results
    if args.query:
        brain_cli.do_query(args.query)
    elif args.cluster:
        brain_cli.do_cluster(args.cluster)
    elif args.plot_clusters:
        clusters = brain.cluster_notes(args.plot_clusters)
        visualizer.plot_clusters(clusters)
    elif args.timeline:
        brain_cli.do_timeline()
    elif args.graph:
        graph = brain.create_graph(args.graph)
        visualizer.plot_graph_with_cytoscape(graph)
    else:
        brain_cli.repl()

if __name__=="__main__":
    main()
