// coordinates all js modules

import { setupNoteEvents } from "./events/notes.js";
import { setupClusterEvents } from "./events/cluster.js";
import { setupModalEvents } from "./events/modals.js";
import { setupSearchEvents } from "./events/search.js";

// get main interactive window
const resultsContainer= document.getElementById("results-content");

setupModalEvents();
setupNoteEvents( resultsContainer );
setupSearchEvents( resultsContainer );
setupClusterEvents( resultsContainer );
