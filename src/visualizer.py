#!/usr/bin/env python3
# visualizer.py
# a module that provides visualization utilities for the brain

from .parser import Note
from .clustering import ClusterResult

import numpy as np
from sklearn.decomposition import PCA
from datetime import datetime

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def plot_clusters(clusters: ClusterResult, dim: int=2) -> None:
    cluster_idx, cluster_embeddings = clusters.get_ordered_embeddings()
    pca_projected_embeddings = PCA(n_components=dim).fit_transform(cluster_embeddings)

    # take the (x, y) or (x, y, z) for each embedding
    z = np.hsplit(pca_projected_embeddings, dim)

    if dim == 2:
        fig, ax = plt.subplots()
    if dim ==3: 
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
    
    ax.scatter(*z, c=cluster_idx)
    plt.show()
    
def plot_timeline(notes: list[Note]):
    times = [note.get_created_time() for note in notes]

    fig, ax = plt.subplots()
    ax.hist(times, bins=20, rwidth=.9)
    plt.show()

