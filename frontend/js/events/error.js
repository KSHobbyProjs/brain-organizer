/* error.js */

import { appState, updateUI } from "../state.js";

export function setupErrorEvents() {
    const errorClose = document.getElementById("close-error-button");
    errorClose.onclick = () => {
        appState.error = null;
        updateUI();
    };
}

