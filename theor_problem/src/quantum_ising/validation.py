"""Numerical validation checks and limiting-case benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb

import numpy as np

from .quantum_basis import ComputationalBasis
from .quantum_hamiltonian import build_sparse_hamiltonian
from .quantum_observables import ObservableSet, compute_observables
from .quantum_solver import GroundStateResult, overlap_magnitude, solve_dense_ground_state, solve_ground_state
from .quantum_symmetry import parity_expectation


@dataclass
class ValidationReport:
    norm_error: float
    parity_expectation: complex
    parity_error: float
    residual: float
    probability_error: float
    distribution_symmetry_error: float
    second_moment_error: float
    correlation_symmetry_error: float
    correlation_diagonal_error: float


def validate_result(
    basis: ComputationalBasis,
    ground_state: GroundStateResult,
    observables: ObservableSet,
    *,
    coupling: float = 1.0,
    g: float | None = None,
    h: float | None = None,
) -> ValidationReport:
    norm_error = float(abs(np.linalg.norm(ground_state.state_full) - 1.0))
    parity = parity_expectation(ground_state.state_full, basis)
    p_values = observables.magnetization_probabilities
    m_values = observables.magnetization_values
    h_full = build_sparse_hamiltonian(basis, coupling=coupling, g=g, h=h, fmt="csr")
    residual = float(np.linalg.norm(h_full @ ground_state.state_full - ground_state.energy * ground_state.state_full) / max(1.0, abs(ground_state.energy)))
    return ValidationReport(
        norm_error=norm_error,
        parity_expectation=parity,
        parity_error=float(abs(parity - 1.0)),
        residual=residual,
        probability_error=float(abs(np.sum(p_values) - 1.0)),
        distribution_symmetry_error=float(np.max(np.abs(p_values - p_values[::-1]))),
        second_moment_error=float(abs(np.dot(m_values**2, p_values) - observables.m_rms**2)),
        correlation_symmetry_error=float(np.max(np.abs(observables.correlation_matrix - observables.correlation_matrix.T))),
        correlation_diagonal_error=float(np.max(np.abs(np.diag(observables.correlation_matrix) - 1.0))),
    )


def dense_sparse_comparison(
    num_sites: int,
    *,
    g: float,
    coupling: float = 1.0,
) -> dict[str, float]:
    basis = ComputationalBasis(num_sites)
    sparse_result = solve_ground_state(basis, coupling=coupling, g=g)
    dense_result = solve_dense_ground_state(basis, coupling=coupling, g=g)
    sparse_obs = compute_observables(sparse_result.state_full, basis)
    dense_obs = compute_observables(dense_result.state_full, basis)
    return {
        "energy_error": abs(sparse_result.energy - dense_result.energy),
        "overlap": overlap_magnitude(sparse_result.state_full, dense_result.state_full),
        "m_rms_error": abs(sparse_obs.m_rms - dense_obs.m_rms),
        "m_x_error": abs(sparse_obs.m_x - dense_obs.m_x),
    }


def ferromagnetic_even_state(basis: ComputationalBasis) -> np.ndarray:
    state = np.zeros(basis.dim, dtype=np.complex128)
    state[0] = 1.0 / np.sqrt(2.0)
    state[basis.mask] = 1.0 / np.sqrt(2.0)
    return state


def g0_ferromagnetic_benchmark(num_sites: int) -> dict[str, float | np.ndarray]:
    basis = ComputationalBasis(num_sites)
    state = ferromagnetic_even_state(basis)
    observables = compute_observables(state, basis, include_basis_probabilities=True)
    h_full = build_sparse_hamiltonian(basis, coupling=1.0, g=0.0, fmt="csr")
    energy = float(np.real(np.vdot(state, h_full @ state)))
    return {
        "energy": energy,
        "mean_mz": observables.mean_mz,
        "m_rms": observables.m_rms,
        "m_x": observables.m_x,
        "correlation_matrix": observables.correlation_matrix,
        "probabilities": observables.magnetization_probabilities,
    }


def independent_spin_benchmark(num_sites: int, *, h: float = 1.7) -> dict[str, float | np.ndarray]:
    basis = ComputationalBasis(num_sites)
    result = solve_ground_state(basis, coupling=0.0, h=h)
    observables = compute_observables(result.state_full, basis)
    expected_distribution = np.array([comb(num_sites, k) for k in range(num_sites + 1)], dtype=np.float64) / (2**num_sites)
    return {
        "energy": result.energy,
        "m_rms": observables.m_rms,
        "m_x": observables.m_x,
        "correlation_matrix": observables.correlation_matrix,
        "distribution": observables.magnetization_probabilities,
        "expected_distribution": expected_distribution,
    }


def hellmann_feynman_check(
    num_sites: int,
    *,
    g: float,
    delta: float,
    coupling: float = 1.0,
) -> dict[str, float]:
    basis = ComputationalBasis(num_sites)
    lower = solve_ground_state(basis, coupling=coupling, g=g - delta)
    center = solve_ground_state(basis, coupling=coupling, g=g)
    upper = solve_ground_state(basis, coupling=coupling, g=g + delta, initial_state=center.state_even)
    observables = compute_observables(center.state_full, basis)
    derivative = (upper.energy - lower.energy) / (2.0 * delta)
    estimate = -(1.0 / num_sites) * derivative
    return {
        "direct_m_x": observables.m_x,
        "hf_estimate": estimate,
        "absolute_error": abs(estimate - observables.m_x),
    }


def solver_tolerance_study(
    num_sites: int,
    *,
    g_values: list[float],
    tolerances: tuple[float, float] = (1e-9, 1e-11),
) -> list[dict[str, float]]:
    basis = ComputationalBasis(num_sites)
    reports: list[dict[str, float]] = []
    for g in g_values:
        coarse = solve_ground_state(basis, g=g, tolerance=tolerances[0])
        fine = solve_ground_state(basis, g=g, tolerance=tolerances[1], initial_state=coarse.state_even)
        coarse_obs = compute_observables(coarse.state_full, basis)
        fine_obs = compute_observables(fine.state_full, basis)
        reports.append(
            {
                "g": g,
                "delta_energy": abs(fine.energy - coarse.energy),
                "delta_m_rms": abs(fine_obs.m_rms - coarse_obs.m_rms),
                "delta_m_x": abs(fine_obs.m_x - coarse_obs.m_x),
                "delta_g_far": abs((fine_obs.g_far or 0.0) - (coarse_obs.g_far or 0.0)),
            }
        )
    return reports
