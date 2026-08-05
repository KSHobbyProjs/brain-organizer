/* error.js */

const errorBox = document.getElementById("error-box");
const errorContent = document.getElementById("error-content");

export function showError(message) {
    errorBox.classList.remove("hidden");
    errorContent.textContent = message;
}

export function clearError() {
    errorBox.classList.add("hidden");
    errorContent.textContent = "";
}
