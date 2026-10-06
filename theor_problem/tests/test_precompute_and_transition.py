from __future__ import annotations

import numpy as np

from quantum_ising.data_precompute import generate_field_grid
from quantum_ising.transition_analysis import refined_field_grid


def test_field_grid_contains_required_snapshot_points() -> None:
    grid = generate_field_grid()
    assert 0.2 in grid
    assert 1.0 in grid
    assert 3.0 in grid


def test_refined_field_grid_stays_bounded() -> None:
    grid = refined_field_grid(0.11, step=0.005, half_width=0.05)
    assert np.all(grid >= 0.1)
    assert np.all(grid <= 3.0)
