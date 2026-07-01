# Brain Organizer
This project is designed to embed personal notes (right now, only Google Keep notes imported with Google Takeover work) with sentence transformers, and perform analysis on this data.

Currently, the following actions may be performed:
 - *Semantic Search*: search for the notes that most closely align with a query search.
 - *Clustering*: cluster the notes into categories based on semantic similarity.  
 - *Visualization*: visualize clusters in 2D or 3D.
 - *Timeline*: produces a histogram of notes taken in time.

---

## Install
Clone the repository and install dependencies:
```bash
git clone https://github.com/KSHobbyProjs/brain-organizer.git
cd brain-organizer
pip install -r requirements.txt
```
Dependencies include `numpy`, `scipy`, `scikit`, `sentence-transformers`, `torch`, `cuda` (preferably), etc.

---

## Usage
- Unzip Google Keep notes exported with Google Takeover
- Run `python main.py path/to/keepnotes`
- Possible command arguments include:
    -  `--query "foo bar"`: searches notes for notes with content best matching "foo bar" and displays the top 5 in terminal.
    - `--cluster 5`       : uses KMeans to produce 5 clusters out of the data and displays three notes in each sector in terminal.
    - `--visualize`       : produces a plot of the embedded notes in 2D / 3D with highlighted clusters.
    - `--timeline`        : produces a histogram of note creation over time.
    - ...
- If run without any command arguments, runs a REPL where the natural mode accepts queries and prints the top notes matching that query, and other functions are available with commands of the style: `:cluster 5`.

---

### Milestones
- [x] Milestone 1: Google Takeout -> JSON
- [x] Milestone 2: JSON -> embeddings
- [x] Milestone 3: semantic search
- [x] Milestone 4: organizer + CLI
- [x] Milestone 5: embeddings -> clusters
- [x] Milestone 6: clusters -> visualization
- [x] Milestone 7: timeline
- [] Milestone 8: AI summaries
- [] Milestone 9: package / documentation
