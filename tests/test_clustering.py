#!/usr/bin/env python3

import pytest
from astropy import units as u


@pytest.mark.skip(reason="clustering_targets is not part of targetdb")
def test_run_clustering():
    ra = [0.0, 0.5, 0.0, 0.5, 0.0, 0.5, 0.0, 0.5]
    dec = [0.0, 0.0, 30.0, 30.0, 60.0, 60.0, 85.0, 85.0]

    threshs = [
        0.51 * u.degree,
        0.49 * u.degree,
        0.26 * u.degree,
        0.24 * u.degree,
        0.04 * u.degree,
    ]

    expected_n_clusters = [4, 5, 6, 7, 8]
    # expected_n_noises = [0, 0, 0, 0, 0]

    returned_n_clusters = []
    # returned_n_noises = []

    for th in threshs:
        labels = clustering_targets.run_clustering(ra, dec, distance_threshold=th)  # noqa: F821
        print(f"{labels=}")
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        # n_noise_ = list(labels).count(-1)

        returned_n_clusters.append(n_clusters_)
        # returned_n_noises.append(n_noise_)

    assert returned_n_clusters == expected_n_clusters
    # assert returned_n_noises == expected_n_noises


if __name__ == "__main__":
    test_run_clustering()
