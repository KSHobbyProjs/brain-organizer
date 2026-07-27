# A module storing the domain objects of the API: Note and Chunk
from dataclasses import dataclass
import datetime

@dataclass
class Note:
    """
    Class for storing data and metadata important to each note.
    """
    title: str
    text: str
    created_time: datetime.date | None = None
    edited_time: datetime.date | None = None
    labels: list[str] | None = None
    is_pinned: bool | None = None
    is_archived: bool | None = None
    is_trashed: bool | None = None

    # get time that note was created
    def get_created_time(self) -> datetime.date | None:
        return self.created_time

    def to_full_note(self) -> str:
        labels_str = " ".join(self.labels)
        note = f"Title: {self.title}\n"
        note += f"Date: {self.created_time}\n"
        note += f"Labels: {self.labels}\n"
        note += self.text
        return note

    def to_dict(self) -> dict:
        return {
                "title": self.title,
                "text": self.text,
                "created_time": (
                    self.created_time.isoformat()
                    if self.created_time
                    else None
                    ),
                "edited_time": (
                    self.edited_time.isoformat()
                    if self.edited_time
                    else None
                    ),
                "labels": self.labels,
                "is_pinned": self.is_pinned,
                "is_archived": self.is_archived,
                "is_trashed": self.is_trashed
            }


@dataclass 
class Chunk:
    """
    A class to store chunk metadata when a note is broken into chunks
    """
    note_id: int
    text: str


