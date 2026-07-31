// events for viewing all notes

import { setMode } from "../state.js";
import { renderNotes, renderFullNote } from "../render/notes.js";
import { getAllNotes } from "../api.js";
import { openModal } from "../ui/modals.js";

const onNoteClick = (note) => {
    openModal(note, renderFullNote);
};

export function setupNoteEvents( resultsContainer ) {
    const button = document.getElementById("note-view-button");
    button.onclick = async () => {
        const result = await getAllNotes();
        setMode("note-mode");
        renderNotes(result, resultsContainer, onNoteClick);
    };
}
