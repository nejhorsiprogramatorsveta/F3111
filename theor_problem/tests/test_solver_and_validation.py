from __future__ import annotations

from quantum_ising.quantum_basis import ComputationalBasis
from quantum_ising.quantum_observables import compute_observables
from quantum_ising.quantum_solver import solve_ground_state
from quantum_ising.validation import dense_sparse_comparison, hellmann_feynman_check, validate_result


def test_sparse_matches_dense_for_small_system() -> None:
    comparison = dense_sparse_comparison(6, g=0.9)
    assert comparison["energy_error"] < 1e-10
    assert comparison["overlap"] > 1 - 1e-10
    assert comparison["m_rms_error"] < 1e-10
    assert comparison["m_x_error"] < 1e-10


def test_validation_report_is_tight() -> None:
    basis = ComputationalBasis(6)
    result = solve_ground_state(basis, g=1.0)
    observables = compute_observables(result.state_full, basis)
    report = validate_result(basis, result, observables, g=1.0)
    assert report.norm_error < 1e-10
    assert report.parity_error < 1e-10
    assert report.residual < 1e-9
    assert report.probability_error < 1e-12
    assert report.distribution_symmetry_error < 1e-10
    assert report.second_moment_error < 1e-12
    assert report.correlation_symmetry_error < 1e-12
    assert report.correlation_diagonal_error < 1e-12


def test_hellmann_feynman_relation_converges() -> None:
    coarse = hellmann_feynman_check(6, g=1.0, delta=1e-2)
    fine = hellmann_feynman_check(6, g=1.0, delta=5e-3)
    assert fine["absolute_error"] < coarse["absolute_error"]
    assert fine["absolute_error"] < 5e-5
