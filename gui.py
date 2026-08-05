#!/usr/bin/env python

import datetime

from src.organizer import BrainOrganizer
from src.schemas import query_results_to_response, cluster_results_to_response

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

from pydantic import BaseModel


class ChunkerOptions(BaseModel):
    soft_min_len: int | None = None
    max_len: int | None = None
    num_tokens: int | None = None
    include_context: bool = False

class LoadSettings(BaseModel):
    directory: str
    parser: str
    embedder: str
    chunker: str
    chunker_options: ChunkerOptions
    metric: str

class AppState:
    brain: BrainOrganizer | None = None
    loading: bool = False

state = AppState()
app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")


def require_brain():
    if state.brain is None:
        raise HTTPException(
                status_code=503,
                detail="No notes loaded"
            )
    return state.brain

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.get("/allnotes")
def get_all_notes():
    brain = require_brain()
    notes = brain.get_notes()
    sorted_notes = sorted(
            notes,
            key=lambda x: x.created_time,
            reverse=True
        )
    return [note.to_dict() for note in sorted_notes]

@app.get("/query")
# the q var must be named q because that's what's sent in the
# fetch request in api.js
def search_notes(q: str):
    brain = require_brain()
    query_results = brain.search_notes(q)
    return query_results_to_response(query_results)

@app.get("/cluster")
def cluster_notes(num_clusters: int):
    # TODO: allow settings for num_clusters (forced 5 right now)
    brain = require_brain()
    cluster_results = brain.cluster_notes(num_clusters)
    return cluster_results_to_response(cluster_results)

@app.post("/loadnotes")
def load_notes(settings: LoadSettings):
    state.loading = True
       
    brain = BrainOrganizer.from_directory(
            directory = settings.directory,
            model_name = settings.embedder,
            metric = settings.metric,
            chunk_method = settings.chunker,
            parser_method = settings.parser,
            chunker_options=settings.chunker_options.model_dump(exclude_none=True)
        )

    state.brain = brain
    state.loading = False
    return {
        "status": "ok",
        "num_notes": len(brain.get_notes())
    }

@app.get("/graphnotes")
def graph_notes():
    brain = require_brain()
    graph = brain.create_graph('mutual-knn')
    # TODO: create scheme to convert networkx -> cytoscape -> json
    # TODO: allow settings for type of graph
    return {"status": "ok"}
