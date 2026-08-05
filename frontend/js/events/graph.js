/* events/graph.js */

import { setMode } from "../state.js";
import { graphNotes } from "../api.js";
import { initializeGraph } from "../ui/graph.js";

export function setupGraphEvents( resultsContainer ) {
    const graphButton = document.getElementById("graph-button");

    graphButton.onclick = async () => {
        const graphData = await graphNotes();
        
        setMode("graph-mode");
        
        initializeGraph(graphData, resultsContainer);
    };

}
