/* settings.js */

import { loadSettings } from "../api.js";

const chunker = document.getElementById("chunker");

function updateChunkOptions() {
    const chunkOptions = document.querySelectorAll(".chunk-options");
    const selected = chunker.value;

    /* ensure hidden exists if selected != option
     * ensure hidden doesn't exist if selected == option */
    chunkOptions.forEach(option => {
        option.classList.toggle(
            "hidden",
            option.dataset.chunker !== selected
        );
    });
}

function getSettings() {
    const directory = document.getElementById("notes-directory");
    const parser = document.getElementById("parser");
    const embedder = document.getElementById("embedder");
    const metric = document.getElementById("metric");

    const selectedChunker = chunker.value;

    let chunker_options = {};
    
    if (selectedChunker === "token_number") {
        chunker_options.num_tokens = Number(document.getElementById("chunk-size").value);
    }

    if (selectedChunker === "smart_paragraphs") {
        chunker_options.soft_min_len = Number(document.getElementById("chunk-min").value);
        chunker_options.max_len = Number(document.getElementById("chunk-max").value);
    }
    
    chunker_options.include_context = document.getElementById("chunking-context").checked;

    return  {
        directory: directory.value,
        parser: parser.value,
        embedder: embedder.value,
        chunker: selectedChunker,
        chunker_options,
        metric: metric.value
    }
}

export function setupSettingsEvents() {
    const settingsModal = document.getElementById("settings-modal");
    /* load notes */
    const button = document.getElementById("load-notes-button"); 
    button.onclick = () => {
        settingsModal.classList.remove("hidden");
    };
   
    /* close settings window */
    const closeButton = document.getElementById("close-settings-button");
    closeButton.onclick = () => {
        settingsModal.classList.add("hidden");
    };

    /* + chunking options based on what's selected */
    chunker.addEventListener("change", updateChunkOptions);
    updateChunkOptions();

    /* submit form when load is clicked */
    const form = document.getElementById("settings-form");
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const settings = getSettings();
        
        const response = await loadSettings(settings);
        settingsModal.classList.add("hidden");
        console.log(response)
    }); 
}
