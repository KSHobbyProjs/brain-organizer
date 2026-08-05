// coordinates all js modules

import { setupNoteEvents } from "./events/notes.js";
import { setupClusterEvents } from "./events/cluster.js";
import { setupModalEvents } from "./events/modals.js";
import { setupSearchEvents } from "./events/search.js";
import { setupSettingsEvents } from "./events/settings.js";
import { setupGraphEvents } from "./events/graph.js";

// get main interactive window
const resultsContainer= document.getElementById("results-content");

setupModalEvents();
setupSettingsEvents();
setupNoteEvents( resultsContainer );
setupSearchEvents( resultsContainer );
setupClusterEvents( resultsContainer );
setupGraphEvents( resultsContainer );
