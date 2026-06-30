#!/usr/bin/env python3
# main.py
# CLI for application

import argparse
import rich.console, rich.rule
from enum import Enum

from src.organizer import BrainOrganizer

class CmdResult(Enum):
    NONE = 0
    CONTINUE = 1
    EXIT = 2

class Mode(Enum):
    QUERY = "query"
    CLUSTER = "cluster"
    TIMELINE = "timeline"

class BrainCLI:
    def __init__(self, brain: BrainOrganizer, top_k: int):
        self.brain = brain
        self.top_k = top_k

        self.console = rich.console.Console()
        self.mode = Mode.QUERY
 
    def handle_commands(self, line: str) -> CmdResult:
        """ Returns 0, 1, 2 after executing command """
        cmd, *args = line[1:].strip().split(" ", 1)
        arg = args[0] if args else ""

        if cmd == "query":
            self.mode = Mode.QUERY
            return CmdResult.CONTINUE
        elif cmd == "cluster":
            self.mode = Mode.CLUSTER
            return CmdResult.CONTINUE
        elif cmd == "timeline":
            self.mode = Mode.TIMELINE
            return CmdResult.CONTINUE

        elif cmd == "clear" or cmd == "cls":
            self.console.clear()
            return CmdResult.CONTINUE
        elif cmd == "exit" or cmd == "quit":
            return CmdResult.EXIT
        else:
            self.console.print(f"[red]{line} is not a recognized command[/red]")
            return CmdResult.CONTINUE

    def print_results(self, results) -> None:
        for i, result in enumerate(results):
            self.console.print(f"[bold cyan]Result # {i+1}[/bold cyan]")
            self.console.print(f"{result.to_preview()}")
            self.console.print(rich.rule.Rule())
 
    def repl(self) -> None:
        while True:
            try:
                # read a line of input
                line = input(f"brain:{self.mode.value}> ")

                # check for command and run command
                if line.startswith(":"):
                    # result can be 0 (do nothing), 1 (continue to next input), 2 (exit program)
                    result = self.handle_commands(line)
                    if result == CmdResult.EXIT:
                        break
                    if result == CmdResult.CONTINUE:
                        continue
                
                # run specific method based on brain mode
                if self.mode == Mode.QUERY:
                    search_results = self.brain.search_notes(line, self.top_k)
                    self.print_results(search_results)
                elif self.mode == Mode.CLUSTER:
                    try:
                        num_clusters = int(line)
                    except ValueError:
                        self.console.print(f"[yellow]{line} cannot be converted to type int[/yellow]")
                        continue
                    clusters = self.brain.cluster_notes(num_clusters)
                    self.print_results(clusters.values())
                elif self.mode == Mode.TIMELINE:
                    self.console.print("[yellow]Timeline mode not supported yet[/yellow]")
                    
 
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
    parser.add_argument('-k', '--top-k', type=int, default=5)
    parser.add_argument('-m', '--model-name', type=str, default='sentence-transformers/all-MiniLM-L6-v2')
    
    args = parser.parse_args()
    brain = BrainOrganizer.from_keep_directory(args.directory, args.model_name)
    brain_cli = BrainCLI(brain, args.top_k)

    # treat the brain as its own interactive model, 
    # but allow a straight query result if prompted with '--query'
    # TODO: if more modes are added, add other catch statements like this
    if args.query:
        search_results = brain.search_notes(args.query, args.top_k)
        brain_cli.print_results(search_results)
    elif args.cluster:
        clusters = brain.cluster_notes(args.cluster)
        brain_cli.print_results(clusters.values())
    else:
        brain_cli.repl()

if __name__=="__main__":
    main()
