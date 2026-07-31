// events for searching tool

import { searchNotes} from "../api.js";
import { setMode } from "../state.js";
import { renderSearchResults, renderFullSearchResult } from "../render/search.js";
import { openModal } from "../ui/modals.js";

const onSearchResultClick = (searchResult) => {
    openModal(searchResult, renderFullSearchResult);
};

export function setupSearchEvents( resultsContainer ) {
    const searchBox = document.getElementById("search-box");
    const queryInput = document.getElementById("query");

    searchBox.addEventListener("submit", async (event) => {
        event.preventDefault();

        const query = queryInput.value;
        const searchResults = await searchNotes(query);
        setMode("note-mode");
        renderSearchResults(searchResults, resultsContainer, onSearchResultClick);
    });
};
