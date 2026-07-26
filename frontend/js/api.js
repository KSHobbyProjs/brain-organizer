// module to handle all api requests

export const getAllNotes = async () => {
    const response = await fetch("/allnotes");
    
    if (!response.ok) {
        throw new Error("Failed to fetch notes.");
    }

    return await response.json();
};
