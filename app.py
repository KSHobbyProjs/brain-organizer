#!/usr/bin/env python

from src.organizer import BrainOrganizer

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/", StaticFiles(directory="gui", html=True), name="index")

