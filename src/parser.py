# parser.py
# A class for parsing Google Keep JSON files into a JSON schema used by the rest of the program.
# Extension to parsing other data can be added.
from pathlib import Path
import json
import datetime
from dataclasses import dataclass

def parse_keep_timestamp(timestamp_usec: str | None) -> datetime.datetime | None:
    if timestamp_usec is None:
        return None

    return datetime.date.fromtimestamp(
            int(timestamp_usec) / 1_000_000
            )

@dataclass
class Note:
    """
    Class for storing data and metadata important to each note.
    """
    title: str
    text: str
    created_time: datetime.datetime | None
    edited_time: datetime.datetime | None
    labels: list[str]
    is_pinned: bool
    is_archived: bool
    is_trashed: bool 

    def to_text(self) -> str:
        # a class to convert the Note object to a string for embedding
        return f"Title: {self.title}\n\n{self.text}"

class KeepParser:
    def __init__(self, keep_directory: str | Path):
        self.keep_dir = Path(keep_directory)
        self.keepjson_files: list[Path] = []
        self.notes: list[Note] = []

        # fail early if path given isn't a directory
        if not self.keep_dir.is_dir():
            raise ValueError(f"{self.keep_dir} is not a valid directory.")

    def get_keepjson_files(self) -> list[Path]:
       keepjson_files = [
               file 
               for file in self.keep_dir.iterdir()
               if file.suffix == ".json"
            ]
       self.keepjson_files = keepjson_files
       return keepjson_files

    def create_notes(self) -> list[Note]:
        notes = []
        for file in self.keepjson_files:
            note = self.create_note_from_keepjson(file)
            notes.append(note)

        self.notes = notes
        return notes

    @staticmethod
    def create_note_from_keepjson(keepjson: Path) -> Note:
        with keepjson.open("r", encoding="utf-8") as f:
            keepjson_data = json.load(f)

        title = keepjson_data.get("title", "")
        text = keepjson_data.get("textContent", "")
        created_time = parse_keep_timestamp(keepjson_data.get("createdTimestampUsec"))
        edited_time = parse_keep_timestamp(keepjson_data.get("userEditedTimestampUsec"))
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

