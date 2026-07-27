// coordinates all js modules

import { getAllNotes, searchNotes } from "./api.js"
import { renderNotes, renderFullNote } from "./notes.js"



// get main interactive window
const resultsContainer= document.getElementById("results-content");
const modalContainer = document.getElementById("modal"); // modal for displaying single notes
const modalContent = document.getElementById("modal-content");

// define what happens when a note is clicked
const openNote = (note) => {
    console.log("Opening note");
    modalContainer.classList.remove("hidden");
    renderFullNote(note, modalContent);
};

// close modal if 'x' is pressed
const modalClose = document.getElementById("close-modal");
modalClose.onclick = () => {
    modalContainer.classList.add("hidden");
};

// button requests to change modes (search, cluster, etc.)
const button = document.getElementById("all-notes");
button.onclick = async () => {
    console.log("All notes button clicked");
    const result = await getAllNotes();
    console.log("Note results recieved");
    renderNotes(result, resultsContainer, openNote);
    console.log("Notes rendered");
};

const searchBox = document.getElementById("search-box");
const queryInput = document.getElementById("query");
searchBox.addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = queryInput.value;
    console.log("Query submitted", query);
    const result = await searchNotes(query);
    console.log("Query results recieved");
    renderNotes(result, resultsContainer, openNote);
});
