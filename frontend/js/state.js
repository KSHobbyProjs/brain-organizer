// module for holding state

export const appState = {
    mode: "note-mode",
    clusters: [],
    currentCluster: 0
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
