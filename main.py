#!/usr/bin/env python3
# main.py
# CLI for application

import argparse
import rich.console, rich.rule
from enum import Enum

from src.organizer import BrainOrganizer
import src.visualizer as visualizer

# only used for type hints
from src.parser import Note
from src.search import SearchResult
from src.clustering import ClusterResult

class CmdResult(Enum):
    NONE = 0      # continue with current iteration
    CONTINUE = 2  # move to next iteration
    EXIT = 1      # break out of repl

class BrainCLI:
    def __init__(self, brain: BrainOrganizer, top_k: int):
        self.brain = brain
        self.top_k = top_k

        self.console = rich.console.Console()

        self._current_query_results: list[SearchResult] | None = None
        self._current_cluster_results: ClusterResult | None = None

        self.commands = {
                "cluster" : self.do_cluster,
                "visualize": self.do_visualize,
                "timeline": self.do_timeline,
                "open" : self.do_open,

                "clear" : self.do_clear,
                "cls" : self.do_clear,

                "exit" : self.do_exit,
                "q" : self.do_exit,
                "quit" : self.do_exit
                }

    # ---------------------------------- COMMANDS for REPL -------------------------------
    def do_query(self, query_txt: str) -> CmdResult:
        search_results: list[SearchResult] = self.brain.search_notes(query_txt, self.top_k)
        self.print_search_results(search_results)
        
        self._current_query_results = search_results # update cache
        return CmdResult.CONTINUE

    def do_cluster(self, num_clusters: str='5') -> CmdResult:
        num_clusters = int(num_clusters)
        cluster_results: ClusterResult = self.brain.cluster_notes(num_clusters)
        self.print_cluster_results(cluster_results)
        
        self._current_cluster_results = cluster_results # update cache
        return CmdResult.CONTINUE

    def do_visualize(self, dim: str='2') -> CmdResult:
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

    def do_open(self, note_num: str='1'):
        idx = int(note_num) - 1
        if self._current_query_results:
            try:
                search_result = self._current_query_results[idx]
            except IndexError:
                self.console.print("[yellow]Requested note is out of range.\n Requesting more notes will be added soon.[/yellow]")
                return CmdResult.CONTINUE
        else:
            self.console.print("[yellow]No notes loaded. Can't run open[/yellow]")
            return CmdResult.CONTINUE


        note = search_result.note
        self.print_fullnote(note)
        return CmdResult.CONTINUE

    def do_clear(self, *args) -> CmdResult:
        self.console.clear()
        return CmdResult.CONTINUE

    def do_exit(self, *args) -> CmdResult:
        return CmdResult.EXIT
 
    def handle_commands(self, line: str) -> CmdResult:
        """ Returns 0, 1, 2 after executing command """
        cmd, *args = line[1:].strip().split(" ")

        func = self.commands.get(cmd)
        if func is None:
            self.console.print(f"[red]{line} is not a recognized command[/red]")
            return CmdResult.CONTINUE
        
        result = func(*args)
        return result

    # ---------------------------------- PRINTING for REPL -------------------------------
    def print_search_results(self, results) -> None:
        for i, result in enumerate(results):
            self.console.print(f"[bold cyan]Result # {i+1}[/bold cyan]")
            self.console.print(f"{result.to_preview()}")
            self.console.print(rich.rule.Rule())

    def print_cluster_results(self, results) -> None:
        self.console.print(f"[blue]Clusters[/blue]")
        self.console.print(rich.rule.Rule())
        self.console.print(results.to_preview())

    def print_fullnote(self, note: Note) -> None:
        self.console.print(note.to_fullnote())

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
    parser = argparse.ArgumentParser(
            prog='SemanticSearcher',
            description='Searches Keep notes for notes that best match a query semantically',
            )
    parser.add_argument('directory', type=str)
    parser.add_argument('-q', '--query', type=str)
    parser.add_argument('-c', '--cluster', type=int)
    parser.add_argument('-v', '--visualize', type=int)
    parser.add_argument('-k', '--top-k', type=int, default=5)
    parser.add_argument('-m', '--model-name', type=str, default='sentence-transformers/all-MiniLM-L6-v2')
    parser.add_argument('-t', '--timeline', action='store_true')
    
    args = parser.parse_args()
    brain = BrainOrganizer.from_keep_directory(args.directory, args.model_name)
    brain_cli = BrainCLI(brain, args.top_k)

    # treat the brain as its own interactive model, 
    # but allow a straight query result if prompted with '--query'
    # the default mode of the repl is to accept queries and spit out results
    if args.query:
        search_results = brain.search_notes(args.query, args.top_k)
        brain_cli.print_search_results(search_results)
    elif args.cluster:
        clusters = brain.cluster_notes(args.cluster)
        brain_cli.print_cluster_results(clusters)
    elif args.visualize:
        clusters = brain.cluster_notes(args.visualize)
        visualizer.plot_clusters(clusters)
    elif args.timeline:
        notes = brain.notes
        visualizer.plot_timeline(notes)
    else:
        brain_cli.repl()

if __name__=="__main__":
    main()
