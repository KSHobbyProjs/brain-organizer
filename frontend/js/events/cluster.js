// module for handling cluster events

import { clusterNotes } from "../api.js";
import { setMode, appState } from "../state.js";
import {renderClusterWindow, renderCluster } from "../render/cluster.js";
import { renderFullSearchResult } from "../render/search.js";
import { openModal } from "../ui/modals.js";

let clusterUI; 

// re-use renderFullSearchResult since the notes
// output in the clusters are rendered in the same way
const onClusterResultClick = (clusterResult) => {
    openModal(clusterResult, renderFullSearchResult);
};

const viewCurrentCluster = () => {
    renderCluster(
        appState.clusters[appState.currentCluster],
        clusterUI,
        onClusterResultClick
    );
};

// when previous / next cluster buttons are clicked
const prevCluster = () => {
    appState.currentCluster = Math.max(
        0,
        appState.currentCluster - 1
    );
    viewCurrentCluster();
};
const nextCluster = () => {
    appState.currentCluster = Math.min(
        appState.clusters.length - 1,
        appState.currentCluster + 1
    );
    viewCurrentCluster();
};

export function setupClusterEvents( resultsContainer ) { 
    const clusterButton = document.getElementById("cluster-button");
    const DEFAULT_NUM_CLUSTERS = 5;

    clusterButton.onclick = async () => {
        const clusterResults = await clusterNotes(DEFAULT_NUM_CLUSTERS);
        appState.clusters = clusterResults;
        setMode("cluster-mode");
        clusterUI = renderClusterWindow(resultsContainer, prevCluster, nextCluster);
        viewCurrentCluster();
    };
}


