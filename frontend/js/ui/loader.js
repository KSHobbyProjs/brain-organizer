/* loader.js */

const loader = document.getElementById("loader");

export function showLoader() {
    loader.classList.remove("hidden");
}

export function hideLoader() {
    loader.classList.add("hidden");

}
