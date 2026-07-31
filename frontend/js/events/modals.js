// setup closing event for modals

import { closeModal } from "../ui/modals.js";

// this only sets up the closing event since the 
// other tools are responsible for opening it
export function setupModalEvents() {
    const modalClose = document.getElementById("close-modal-button");
    modalClose.onclick = () => {
        closeModal();
    };
}
