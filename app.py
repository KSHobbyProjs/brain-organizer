#!/usr/bin/env python

from src.organizer import BrainOrganizer

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

brain = BrainOrganizer.from_keep_directory(keep_dir='tests/keep/')


app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.get("/allnotes")
def get_all_notes():
    return [note.to_dict() for note in brain.get_notes()]

