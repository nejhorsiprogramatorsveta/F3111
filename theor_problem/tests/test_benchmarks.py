from __future__ import annotations

import numpy as np

from quantum_ising.validation import g0_ferromagnetic_benchmark, independent_spin_benchmark


def test_g0_ferromagnetic_benchmark() -> None:
    benchmark = g0_ferromagnetic_benchmark(6)
    assert np.isclose(benchmark["energy"], -6.0)
    assert np.isclose(benchmark["mean_mz"], 0.0)
    assert np.isclose(benchmark["m_rms"], 1.0)
    assert np.isclose(benchmark["m_x"], 0.0)
    assert np.allclose(benchmark["correlation_matrix"], 1.0)
    assert np.allclose(benchmark["probabilities"], np.array([0.5, 0, 0, 0, 0, 0, 0.5]))


def test_independent_spin_benchmark() -> None:
    benchmark = independent_spin_benchmark(6, h=1.2)
    assert np.isclose(benchmark["energy"], -7.2, atol=1e-8)
    assert np.isclose(benchmark["m_x"], 1.0, atol=1e-8)
    assert np.isclose(benchmark["m_rms"], 1 / np.sqrt(6), atol=1e-8)
    assert np.allclose(benchmark["correlation_matrix"], np.eye(6), atol=1e-8)
    assert np.allclose(benchmark["distribution"], benchmark["expected_distribution"], atol=1e-8)
