"""Ground-state observables and exact magnetization distributions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .quantum_basis import ComputationalBasis


@dataclass
class ObservableSet:
    mean_mz: float
    m_rms: float
    m_x: float
    correlation_matrix: np.ndarray
    g_far: float | None
    magnetization_values: np.ndarray
    magnetization_probabilities: np.ndarray
    basis_probabilities: np.ndarray | None = None


def basis_probabilities(state_full: np.ndarray) -> np.ndarray:
    return np.abs(state_full) ** 2


def magnetization_distribution(probabilities: np.ndarray, basis: ComputationalBasis) -> tuple[np.ndarray, np.ndarray]:
    counts = np.bincount(basis.popcounts, weights=probabilities, minlength=basis.num_sites + 1)
    m_values = 1.0 - 2.0 * np.arange(basis.num_sites + 1, dtype=np.float64) / basis.num_sites
    return m_values, counts.astype(np.float64, copy=False)


def transverse_magnetization(state_full: np.ndarray, basis: ComputationalBasis) -> float:
    expectation = 0.0 + 0.0j
    for site in range(basis.num_sites):
        expectation += np.vdot(state_full, state_full[basis.flipped_states(site)])
    value = np.real_if_close(expectation / basis.num_sites)
    return float(np.real(value))


def correlation_matrix(probabilities: np.ndarray, basis: ComputationalBasis) -> np.ndarray:
    z_values = basis.z_values.astype(np.float64, copy=False)
    weighted_z = probabilities[:, None] * z_values
    return z_values.T @ weighted_z


def long_distance_correlation(correlations: np.ndarray) -> float | None:
    size = correlations.shape[0]
    if size % 2 != 0:
        return None
    indices = np.arange(size)
    return float(np.mean(correlations[indices, (indices + size // 2) % size]))


def compute_observables(
    state_full: np.ndarray,
    basis: ComputationalBasis,
    *,
    include_basis_probabilities: bool = False,
) -> ObservableSet:
    probabilities = basis_probabilities(state_full)
    mean_mz = float(np.dot(probabilities, basis.magnetization_basis))
    second_moment = float(np.dot(probabilities, basis.magnetization_basis**2))
    m_values, p_values = magnetization_distribution(probabilities, basis)
    correlations = correlation_matrix(probabilities, basis)
    return ObservableSet(
        mean_mz=mean_mz,
        m_rms=float(np.sqrt(max(second_moment, 0.0))),
        m_x=transverse_magnetization(state_full, basis),
        correlation_matrix=correlations,
        g_far=long_distance_correlation(correlations),
        magnetization_values=m_values,
        magnetization_probabilities=p_values,
        basis_probabilities=probabilities if include_basis_probabilities else None,
    )


def sample_measurements(
    state_full: np.ndarray,
    basis: ComputationalBasis,
    *,
    num_samples: int,
    seed: int | None = None,
) -> np.ndarray:
    probabilities = basis_probabilities(state_full)
    rng = np.random.default_rng(seed)
    states = rng.choice(basis.dim, size=num_samples, p=probabilities)
    return basis.z_values[states]
