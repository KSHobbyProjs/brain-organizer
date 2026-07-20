#!/usr/bin/env python3
# visualizer.py
# a module that provides visualization utilities for the brain

from .models import Note
from .organizer import ClusterResult

import numpy as np
from sklearn.decomposition import PCA
from datetime import datetime
import networkx as nx
import py4cytoscape as p4c

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def plot_clusters(cluster_results: list[ClusterResult], dim: int=2) -> None:
    # TODO Fix the label portion (right now, it just repeatedly prints the same label)
    """
    Plots a PCA visualization of created clusters

    Parameters
    ----------
    cluster_results : list[ClusterResult]
        note and embedding data for each cluster. Shape (n, d) for n embeddings. 

    Returns
    -------
    None

    Note
    ----
    Produces a plot using matplotlib.
    """
    # convert list of ClusterResults to embeddings and color_idx
    embeddings = np.concatenate([r.embeddings for r in cluster_results], axis=0)
    cluster_idx = [r.cluster_id for r in cluster_results for _ in range(len(r.embeddings))]
    labels = [r.representative_text for r in cluster_results]
    pca_projected_embeddings = PCA(n_components=dim).fit_transform(embeddings)

    # take the (x, y) or (x, y, z) for each embedding
    z = np.hsplit(pca_projected_embeddings, dim)

    if dim == 2:
        fig, ax = plt.subplots()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    elif dim ==3: 
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        #ax.set_frame_on(False)
        ax.set_zticks([-1, 1])
    else:
        raise ValueError(f"dim can only be 2 or 3. got {dim}")

    ax.set_xticks([-1, 1])
    ax.set_yticks([-1, 1])
    ax.scatter(*z, c=cluster_idx, label=labels)
    # ax.legend()
    plt.show()
    
def plot_timeline(notes: list[Note]):
    """
    Plots a timeline of the different notes over time in the form of a histogram
    """
    times = [note.get_created_time() for note in notes]

    fig, ax = plt.subplots()
    ax.hist(times, bins=20, rwidth=.9)
    plt.show()

# TODO: change this so that it doesn't implicitly rely on nx.Graph
#       i.e., add an adapt layer that converts the graph into 
#       my own representation, then pass that here
def plot_graph_with_cytoscape(graph: nx.Graph):
    try:
        p4c.cytoscape_ping()
    except Exception:
        return False
    p4c.create_network_from_networkx(graph, title="Semantic Note Graph")
    p4c.layouts.layout_network('force-directed')
    p4c.create_view()
    return True

def change_cytoscape_coloring_basedon_communities(graph: nx.Graph, label='community_id'):
    """ This method assumes that there's already a graph with community labels present """
    num_communities = np.max([graph.nodes[i][label] for i in range(len(graph.nodes))]) + 1
    colors = [
            "#%02x%02x%02x" % tuple(int(255*x) for x in plt.cm.hsv(i / num_communities)[:3])
            for i in range(num_communities)
        ]

    p4c.set_node_color_mapping(
            table_column="community_id",
            table_column_values=list(range(num_communities)),
            colors=colors
        )

                        
   



