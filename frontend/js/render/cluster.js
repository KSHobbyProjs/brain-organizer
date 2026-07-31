// render functions for clusters

import { renderFullNote } from "./notes.js";
import { renderSearchResults } from "./search.js";

export const renderCluster = (clusterResult, clusterUI, onClick) => {
    const analysisContainer = clusterUI.clusterAnalysis;
    const notesContainer = clusterUI.clusterNoteResults;
    analysisContainer.innerHTML = "";
    notesContainer.innerHTML = "";

    const analysisTitle = document.createElement("h3");
    const analysisStats = document.createElement("div");
    const representativeText = document.createElement("h4");
    const numNotes = document.createElement("h4");
    const radiusStat = document.createElement("h4");
    const densityStat = document.createElement("h4");
    
    const representativeNote = document.createElement("div"); 
    renderFullNote(clusterResult.repNote, representativeNote);

    analysisTitle.textContent = `Cluster ${clusterResult.clusterID+1}`;
    representativeText.textContent = `Topic: ${clusterResult.repText}`;
    numNotes.textContent = `(# chunks, # notes): 
                        (${clusterResult.numChunks}, ${clusterResult.numNotes})`;
    radiusStat.textContent = `Radius: ${clusterResult.radius.toFixed(3)}`;
    densityStat.textContent = `Density: ${clusterResult.density.toFixed(3)}`;
   
    analysisStats.appendChild(analysisTitle);
    analysisStats.appendChild(representativeText);
    analysisStats.appendChild(numNotes);
    analysisStats.appendChild(radiusStat);
    analysisStats.appendChild(densityStat);

    analysisStats.className = "cluster-statblock";
    representativeNote.className = "cluster-repnote";
    analysisContainer.appendChild(analysisStats);
    analysisContainer.appendChild(representativeNote);

    renderSearchResults(clusterResult.contents, notesContainer, onClick);
};

export const renderClusterWindow = (container, prevClick, nextClick) => {
    container.innerHTML = "";

    const buttons = document.createElement("div");
    const prevBttn = document.createElement("button");
    const nextBttn = document.createElement("button");

    prevBttn.onclick = () => prevClick();
    prevBttn.textContent = "<";
    nextBttn.onclick = () => nextClick();
    nextBttn.textContent = ">";
    buttons.appendChild(prevBttn);
    buttons.appendChild(nextBttn);

    const clusterAnalysis = document.createElement("div");
    const clusterNoteResults = document.createElement("div");

    container.appendChild(buttons);
    container.appendChild(clusterAnalysis);
    container.appendChild(clusterNoteResults);

    buttons.className = "cluster-controls";
    clusterAnalysis.className = "cluster-analysis";
    clusterNoteResults.className = "cluster-notes";

    return {
        clusterAnalysis,
        clusterNoteResults
    };    
};

