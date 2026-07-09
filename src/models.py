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
    created_time: datetime.date | None
    edited_time: datetime.date | None
    labels: list[str]
    is_pinned: bool
    is_archived: bool
    is_trashed: bool 

    # get time that note was created
    def get_created_time(self) -> datetime.date:
        return self.created_time

@dataclass 
class Chunk:
    """
    A class to store chunk metadata when a note is broken into chunks
    """
    note_id: int
    text: str


