from __future__ import annotations

import numpy as np

from quantum_ising.quantum_basis import ComputationalBasis
from quantum_ising.quantum_observables import compute_observables
from quantum_ising.quantum_solver import solve_ground_state
from quantum_ising.validation import ferromagnetic_even_state


def test_probability_distribution_and_second_moment_identity() -> None:
    basis = ComputationalBasis(6)
    result = solve_ground_state(basis, g=1.0)
    observables = compute_observables(result.state_full, basis)
    assert np.isclose(observables.magnetization_probabilities.sum(), 1.0)
    second_moment = np.dot(observables.magnetization_values**2, observables.magnetization_probabilities)
    assert np.isclose(second_moment, observables.m_rms**2)


def test_correlation_matrix_is_symmetric_with_unit_diagonal() -> None:
    basis = ComputationalBasis(6)
    result = solve_ground_state(basis, g=0.8)
    observables = compute_observables(result.state_full, basis)
    assert np.allclose(observables.correlation_matrix, observables.correlation_matrix.T)
    assert np.allclose(np.diag(observables.correlation_matrix), 1.0)


def test_mx_for_even_ferromagnetic_state_is_zero() -> None:
    basis = ComputationalBasis(5)
    observables = compute_observables(ferromagnetic_even_state(basis), basis)
    assert np.isclose(observables.m_x, 0.0)
