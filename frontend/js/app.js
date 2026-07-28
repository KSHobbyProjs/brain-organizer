// coordinates all js modules

import { getAllNotes, searchNotes, clusterNotes } from "./api.js"
import { renderNotes, renderFullNote, renderSearchResults, renderFullSearchResult, renderClusters } from "./notes.js"



// get main interactive window
const resultsContainer= document.getElementById("results-content");
const modalContainer = document.getElementById("modal"); // modal for displaying single notes
const modalContent = document.getElementById("modal-content");

// define what happens when certain results are clicked
// when a note is clicked
const openNote = (note) => {
    console.log("Opening note");
    modalContainer.classList.remove("hidden");
    renderFullNote(note, modalContent);
};
// when a search result is clicked
const openSearchResult = (searchResult) => {
    console.log("Opening search result.");
    modalContainer.classList.remove("hidden");
    renderFullSearchResult(searchResult, modalContent);
};
// when a cluster result is clicked
const openClusterResults = (clusterResult) => {
    // TODO: Finish this
    console.log("Opening cluster result")
};

// close modal if 'x' is pressed
const modalClose = document.getElementById("close-modal");
modalClose.onclick = () => {
    modalContainer.classList.add("hidden");
};

// button requests to change modes (search, cluster, etc.)
// get all notes
const button = document.getElementById("all-notes"); 
button.onclick = async () => {
    console.log("All notes button clicked");
    const result = await getAllNotes();
    console.log("Note results recieved");
    renderNotes(result, resultsContainer, openNote);
    console.log("Notes rendered");
};
// search notes
const searchBox = document.getElementById("search-box");
const queryInput = document.getElementById("query");
searchBox.addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = queryInput.value;
    console.log("Query submitted", query);
    const searchResults = await searchNotes(query);
    console.log("Query results recieved");
    renderSearchResults(searchResults, resultsContainer, openSearchResult);
});
// cluster notes
const clusterBttn = document.getElementById("cluster");
const TEMPORARY = 5;
clusterBttn.onclick = async () => {
    console.log("Cluster button clicked");
    const result = await clusterNotes(TEMPORARY);
    console.log("Clusters loaded");
    renderClusters(result, resultsContainer, openClusterResults);
};
