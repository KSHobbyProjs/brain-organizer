// Render functions for search results

export const renderFullSearchResult = (searchResult, container) => {
    console.log(`Score: ${searchResult.chunks[0].score}`);
    console.log(`Num chunks: ${searchResult.chunks.length}`);
    container.innerHTML = "";

    const note = searchResult.note;
    const chunks = searchResult.chunks.sort((a, b) => a.span[0] - b.span[0]); // sort by chunk position

    const noteTitle = document.createElement("h3");
    noteTitle.textContent = note.title;

    const noteDate = document.createElement("h4");
    noteDate.textContent = note.created_time;
    
    const noteText = document.createElement("p");
  
    let html = "";
    let cursor = 0; 
    for (let i = 0; i < chunks.length; i++) {
        const [start, end] = chunks[i].span;
        html += note.text.slice(cursor, start);
        html += "<mark>";
        html +=  note.text.slice(start, end);
        html += "</mark>";
        cursor = end;
    }
    html += note.text.slice(cursor);
    noteText.innerHTML = html;
    
    container.appendChild(noteTitle);
    container.appendChild(noteDate);
    container.append(noteText);
};

export const renderSearchResults = (searchResults, container, onClick) => {
    container.innerHTML = "";
    const context = 50;
    
    for (let i = 0; i < searchResults.length; i++) { 

        const searchResult = searchResults[i];
        
        // only fill view with best match (stored at 0 idx)
        const chunkPos = searchResult.chunks[0].span;
        const note = searchResult.note;
        const start = Math.max(0, chunkPos[0] - context);
        const end = Math.min(note.text.length, chunkPos[1] + context);

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
