#!/usr/bin/env python3
# visualizer.py
# a class that provides visualization utilities for the brain

from .parser import Note
from .clustering import ClusterResult

import numpy as np
from sklearn.decomposition import PCA

def plot_clusters(clusters: dict[int, ClusterResult], dim: int=2) -> None:
    cluster_embeddings = []
    cluster_nums, cluster = clusters.items()
    = PCA(n_components=dim).fit_transform(cluster)
     

def plot_timeline():
    pass

