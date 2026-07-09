#!/usr/bin/env python3
# visualizer.py
# a module that provides visualization utilities for the brain

from .parser import Note

import numpy as np
from sklearn.decomposition import PCA
from datetime import datetime

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def plot_clusters(embeddings: np.ndarray, cluster_idx: list[int], dim: int=2) -> None:
    """
    Plots a PCA visualization of created clusters

    Parameters
    ----------
    embeddings : np.ndarray
        Shape (n, d) for n embeddings. 

    cluster_dix : list[int]
        List mapping each embedding to a specific cluster.
        e.g. cluster_idx[5] = 2 -> embeddings[5, :] belongs to cluster 2.

    Returns
    -------
    None

    Note
    ----
    Produces a plot using matplotlib.
    """
    pca_projected_embeddings = PCA(n_components=dim).fit_transform(embeddings)

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
    """
    Plots a timeline of the different notes over time in the form of a histogram
    """
    times = [note.get_created_time() for note in notes]

    fig, ax = plt.subplots()
    ax.hist(times, bins=20, rwidth=.9)
    plt.show()

