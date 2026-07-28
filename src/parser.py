# parser.py
# A class for parsing Google Keep JSON files into a JSON schema used by the rest of the program.
# Extension to parsing other data can be added.
from pathlib import Path
import json
import datetime

import datetime
from .models import Note

def _validate_dir(directory: str | Path):
    directory = Path(directory)
    # fail early if path given isn't a directory
    if not directory.is_dir():
        raise ValueError(f"{directory} is not a valid directory.")
    return directory

def parse_notes(directory: str | Path, parser: str):
    try:
        parser_func = PARSERS[parser]
    except KeyError:
        raise ValueError(f"'{parser}' not a known parser model.")

    directory = _validate_dir(directory)
    notes: list[Note] = []
    for file in directory.iterdir():
        if file.suffix == ".json":
            note = parser_func(file)
            notes.append(note)
    return notes

def _create_note_from_keepjson(keepjson: Path) -> Note:
    with keepjson.open("r", encoding="utf-8") as f:
        keepjson_data = json.load(f)

    title = keepjson_data.get("title", "")
    text = keepjson_data.get("textContent", "")
    created_time = _parse_keep_timestamp(keepjson_data.get("createdTimestampUsec"))
    edited_time = _parse_keep_timestamp(keepjson_data.get("userEditedTimestampUsec"))
    labels = [label["name"] for label in keepjson_data.get("labels", [])]
    is_trashed = keepjson_data.get("isTrashed", False)
    is_pinned = keepjson_data.get("isPinned", False)
    is_archived = keepjson_data.get("isArchived", False)

    note = Note(
            title=title,
            text=text,
            created_time=created_time,
            edited_time=edited_time,
            labels=labels,
            is_pinned=is_pinned,
            is_archived=is_archived,
            is_trashed=is_trashed
            )
    return note

def _parse_keep_timestamp(timestamp_usec: str | None) -> datetime.datetime | None:
    if timestamp_usec is None:
        return None

    return datetime.date.fromtimestamp(
            int(timestamp_usec) / 1_000_000
            )

def _create_note_from_llmjson(llmjson: Path) -> Note:
    with llmjson.open("r", encoding="utf-8") as f:
        llmjson_data = json.load(f)

    title = llmjson_data.get("title")
    date = datetime.date.fromisoformat(llmjson_data.get("date"))
    text = llmjson_data.get("text")
    labels = llmjson_data.get("labels")
    return Note(
            title=title,
            text=text,
            created_time=date,
            labels=labels
        )

PARSERS = {
        "keep" : _create_note_from_keepjson,
        "llm" : _create_note_from_llmjson,
    }



