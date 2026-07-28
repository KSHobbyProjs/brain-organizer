// search / results UI
// render functions (only responsible for deciding how data is formatted in
// the container. All style handled by CSS.

export const renderNotes = (results, container, onClick) => {
    container.innerHTML = "";

    for (let i = 0; i < results.length; i++) {
        const note = results[i];

        const noteDiv = document.createElement("div");
        noteDiv.className = "note";

        const noteTitle = document.createElement("h3");
        noteTitle.textContent = note.title;

        const noteDate = document.createElement("h4");
        noteDate.textContent = note.created_time;

        const noteText = document.createElement("p");
        noteText.textContent = 
            note.text.slice(0, 300) + 
            (note.text.length > 300 ? "..." : "");
        noteDiv.appendChild(noteTitle);
        noteDiv.appendChild(noteDate);
        noteDiv.appendChild(noteText);

        noteDiv.onclick = () => onClick(note);

        container.appendChild(noteDiv);
    }
};


export const renderFullNote = (note, container) => {
    container.innerHTML = "";    

    const noteTitle = document.createElement("h3");
    noteTitle.textContent = note.title;

    const noteDate = document.createElement("h4");
    noteDate.textContent = note.created_time;

    const noteText = document.createElement("p");
    noteText.textContent = note.text;

    container.appendChild(noteTitle);
    container.appendChild(noteDate);
    container.appendChild(noteText);
};

export const renderFullSearchResult = (searchResult, container) => {
    container.innerHTML = "";

    const {note, chunkPos} = searchResult;

    const noteTitle = document.createElement("h3");
    noteTitle.textContent = note.title;

    const noteDate = document.createElement("h4");
    noteDate.textContent = note.created_time;
    
    const noteText = document.createElement("p");
    noteText.innerHTML = 
        note.text.slice(0, chunkPos[0]) + 
        "<mark>" + 
        note.text.slice(chunkPos[0], chunkPos[1]) +
        "</mark>" + 
        note.text.slice(chunkPos[1], note.text.length);
    
    container.appendChild(noteTitle);
    container.appendChild(noteDate);
    container.append(noteText);
};

export const renderSearchResults = (searchResults, container, onClick) => {
    container.innerHTML = "";
    const context = 50;
    
    for (let i = 0; i < searchResults.length; i++) { 

        const searchResult = searchResults[i];
        const {note, chunkPos} = searchResult;

        const start = Math.max(0, chunkPos[0] - context);
        const end = Math.min(note.text.length, chunkPos[0]);

        const noteDiv = document.createElement("div");
        noteDiv.className = "note";

        const noteTitle = document.createElement("h3");
        noteTitle.textContent = note.title;

        const noteDate = document.createElement("h4");
        noteDate.textContent = note.created_time;

        const noteText = document.createElement("p");
        noteText.innerHTML=
            (start > 0 ? "..." : "") +
            note.text.slice(start, chunkPos[0]) + 
            "<mark>" + 
            note.text.slice(chunkPos[0], chunkPos[1]) +
            "</mark>" + 
            note.text.slice(chunkPos[1], end) + 
            (end < note.text.length ? "..." : "");
                                        
        noteDiv.appendChild(noteTitle);
        noteDiv.appendChild(noteDate);
        noteDiv.appendChild(noteText);

        noteDiv.onclick = () => onClick(searchResult);

        container.appendChild(noteDiv);
    }
};

export const renderClusters = (clusterResult, container, onClick) => {
    console.log("reached renderer");
};
