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
        noteText.textContent = note.text.slice(0, 300) + "...";

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
