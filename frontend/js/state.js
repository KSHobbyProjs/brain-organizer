/* state.js */

import { showLoader, hideLoader } from "./ui/loader.js";
import { showError, clearError } from "./ui/error.js";

export const appState = {
    mode: "note-mode",
    clusters: [],
    currentCluster: 0,
    loaded: false,
    loading: false,
    error: null
};

// for changing state mode and updating page to reflect that
export const setMode = (mode) => {
    appState.mode = mode;
    
    const modeTitle = document.getElementById("mode-title");
    
    document.body.className = mode;

    // this is a switch statement
    modeTitle.textContent = {
        "note-mode" : "Note View",
        "cluster-mode" : "Cluster View",
        "graph-mode" : "Graph View"
    }[mode] ?? "Unknown View";
};

const noteViewBttn = document.getElementById("note-view-button");
const clusterBttn = document.getElementById("cluster-button");
const graphBttn = document.getElementById("graph-button");
const searchBox = document.getElementById("search-box");

export const updateUI = () => {
    noteViewBttn.disabled = !appState.loaded;
    clusterBttn.disabled = !appState.loaded;
    graphBttn.disabled = !appState.loaded;
    searchBox.disabled = !appState.loaded;
    
    if (appState.loading) {
        showLoader();
    } else {
        hideLoader();
    }

    if (appState.error) {
        showError(appState.error);
    } else {
        clearError();
    }

};
