// module to handle all api requests

export const getAllNotes = async () => {
    const response = await fetch("/allnotes");
    
    if (!response.ok) {
        throw new Error("Failed to fetch notes.");
    }

    return await response.json();
};

export const searchNotes = async (query) => {
    // encode just converts the str into something HTTP safe ('q & m?' might become q%20%50%20m%70)
    // the url pattern of ?q=... is standard practice. The part after ? is called the query string
    // (unrelated to the "query" in this program). It's split into key=val pairs. FastAPI automatically
    // parses this. ?q=to&limit=20 is auto read as {q : to, limit : 20}
    const response = await fetch(`/query?q=${encodeURIComponent(query)}`);

    if (!response.ok) {
        throw new Error("Failed to search notes.");
    }
    return await response.json();
};

export const clusterNotes = async (numClusters) => {
    const response = await fetch(`/cluster?num_clusters=${numClusters}`);

    if (!response.ok) { 
        throw new Error("Failed to cluster notes.");
    }
    return await response.json();
};

export const loadSettings = async (settings) => {
    const response = await fetch("/loadnotes", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(settings)
    });

    if (!response.ok) {
        throw new Error("Failed to load notes.");
    }
    return await response.json();
};

export const graphNotes = async () => {
    const response = await fetch("/graphnotes");

    if (!response.ok) {
        throw new Error("Failed to graph notes.");
    }
    return await response.json();
};

