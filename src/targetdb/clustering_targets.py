#!/usr/bin/env python


# import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
# from matplotlib.patches import Circle
# from numpy.random import default_rng
from sklearn import metrics
# from sklearn.cluster import DBSCAN
# from sklearn.cluster import OPTICS
from sklearn.cluster import AgglomerativeClustering
# from sklearn.datasets import make_blobs
from sklearn.metrics.pairwise import haversine_distances

# from sklearn.neighbors import VALID_METRICS
# from sklearn.preprocessing import StandardScaler


def run_clustering(ra, dec, distance_threshold=0.3 * u.arcsec):
    """_summary_

    Parameters
    ----------
    ra : _type_
        _description_
    dec : _type_
        _description_
    distance_threshold : _type_, optional
        _description_, by default 0.3*u.arcsec
    """

    X = np.array([dec, ra]).T
    labels_true = np.zeros_like(dec)

    clustering = AgglomerativeClustering(
        n_clusters=None,
        affinity=haversine_distances,
        linkage="average",
        distance_threshold=distance_threshold.to("radian").value,
        compute_full_tree=True,
    ).fit(np.radians(X))
    # core_samples_mask = np.zeros_like(clustering.labels_, dtype=bool)
    # core_samples_mask = np.ones_like(clustering.labels_, dtype=bool)
    # core_samples_mask[clustering.core_sample_indices_] = True
    labels = clustering.labels_


if __name__ == "__main__":
    pass
