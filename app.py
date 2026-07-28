#!/usr/bin/env python

import datetime

from src.organizer import BrainOrganizer

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

brain = BrainOrganizer.from_directory('tests/llm-notes/')


app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.get("/allnotes")
def get_all_notes():
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
    query_results = brain.search_notes(q);
    results = []
    for query in query_results:
        result = {
                "note" : query.note.to_dict(),
                "chunkPos": query.chunk_pos
            }
        results.append(result)
    return results

