// coordinates all js modules

import { getAllNotes } from "./api.js"
import { renderNotes } from "./notes.js"

// get main interactive window
const resultsContainer= document.getElementById("results-content")

// button requests to change modes (search, cluster, etc.)
const button = document.getElementById("all-notes");
button.onclick = async () => {
    console.log("All notes button clicked");
    const result = await getAllNotes();
    console.log("Note results recieved");
    renderNotes(result, resultsContainer);
    console.log("Notes rendered");
};


