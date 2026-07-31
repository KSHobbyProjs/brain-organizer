// render functions for notes
// render functions (only responsible for deciding how data is formatted in
// the container. All style handled by CSS.

export const renderNotes = (notes, container, onClick) => {
    container.innerHTML = "";

    for (let i = 0; i < notes.length; i++) {
        const note = notes[i];

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
