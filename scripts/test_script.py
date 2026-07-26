#!/usr/bin/env python3 

import numpy as np
from src.organizer import BrainOrganizer
from src.visualizer import plot_graph_with_cytoscape


brain = BrainOrganizer.from_keep_directory("/home/keanan/brain-organizer/tests/keep/")

# Testing graph capabilities
"""
print("creating knn graph")
brain.grapher.create_knn_graph()
print("creating mutual knn graph")
brain.grapher.create_mutual_knn_graph()
print("creating threshold graph")
brain.grapher.create_threshold_graph()
print("creating hairball graph")
brain.grapher.create_hairball_graph()
"""

# testing graph visualization
brain.grapher.create_threshold_graph(.8)
plot_graph_with_cytoscape(brain.grapher.graph)

# testing chunking
chunks = brain.get_chunks()
nn = [] # number of double spaces in text
text_len = [] # length of text
ss = [] # number of times there were occurences of more than 3 spaces
for chunk in chunks:
    text = chunk.text
    nn.append(len(text.strip().split('\n\n')))
    text_len.append(len(text))
    ss.append(len(text.strip().split("  ")))

nn = np.array(nn)
text_len = np.array(text_len)
ss = np.array(ss)

labels = ["double new line characters",
          "length of text",
          "double space characters"
          ]
for i, data in enumerate([nn, text_len, ss]):
    min_, max_ = np.min(data), np.max(data)
    avg, std = np.mean(data), np.std(data)
    print(f"(Min, Max, Mean, Std) for {labels[i]}:"
          f"({min_}, {max_}, {avg:.3f}, {std:.3f})"
          )

print("-----------------------")
print(chunks[np.random.randint(0, len(chunks))].text)
print("-----------------------")
print(chunks[np.random.randint(0, len(chunks))].text)
print("-----------------------")
print(chunks[np.random.randint(0, len(chunks))].text)

# Testing clusterer stuff
from src.clusterer import Clusterer
embeds = np.random.rand(3000, 300)
a = Clusterer(embeds)
a.fit_clusters(5)
print(a.get_centroids()[0].shape)
print(a.to_distance_space().shape)
print(a.get_representative_embeddings())
print(a.compute_radius())
print(a.compute_density())

