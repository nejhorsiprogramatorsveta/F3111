"""Even-parity ground-state eigensolver and solver diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import numpy as np
from scipy import linalg
from scipy.sparse.linalg import eigsh

from .quantum_basis import ComputationalBasis
from .quantum_hamiltonian import build_dense_hamiltonian, build_even_sector_hamiltonian
from .quantum_symmetry import phase_align, reconstruct_full_state


@dataclass
class GroundStateResult:
    energy: float
    state_even: np.ndarray
    state_full: np.ndarray
    residual: float
    sector_dimension: int
    full_dimension: int
    tolerance: float


@dataclass
class DenseGroundStateResult:
    energy: float
    state_full: np.ndarray


def _normalized(state: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(state)
    if norm == 0:
        raise ValueError("zero vector cannot be normalized")
    return state / norm


def eigenpair_residual(hamiltonian, state: np.ndarray, energy: float) -> float:
    defect = hamiltonian @ state - energy * state
    return float(np.linalg.norm(defect) / max(1.0, abs(energy)))


def solve_ground_state(
    basis: ComputationalBasis,
    *,
    coupling: float = 1.0,
    g: float | None = None,
    h: float | None = None,
    tolerance: float = 1e-10,
    maxiter: int | None = None,
    initial_state: np.ndarray | None = None,
) -> GroundStateResult:
    h_even = build_even_sector_hamiltonian(basis, coupling=coupling, g=g, h=h, fmt="csr")
    if initial_state is not None:
        trial_vector = np.real_if_close(initial_state)
        initial_vector = np.asarray(trial_vector, dtype=np.float64)
    else:
        initial_vector = None

    eigenvalues, eigenvectors = eigsh(
        h_even,
        k=1,
        which="SA",
        tol=cast(Any, tolerance),
        maxiter=maxiter,
        v0=initial_vector,
    )
    energy = float(eigenvalues[0])
    state_even = phase_align(_normalized(eigenvectors[:, 0]))
    state_full = reconstruct_full_state(state_even, basis)
    residual = eigenpair_residual(h_even, state_even, energy)
    return GroundStateResult(
        energy=energy,
        state_even=state_even,
        state_full=state_full,
        residual=residual,
        sector_dimension=basis.even_dim,
        full_dimension=basis.dim,
        tolerance=tolerance,
    )


def solve_dense_ground_state(
    basis: ComputationalBasis,
    *,
    coupling: float = 1.0,
    g: float | None = None,
    h: float | None = None,
) -> DenseGroundStateResult:
    dense_h = build_dense_hamiltonian(basis, coupling=coupling, g=g, h=h)
    eigenvalues, eigenvectors = linalg.eigh(dense_h)
    state = phase_align(_normalized(eigenvectors[:, 0]))
    return DenseGroundStateResult(energy=float(eigenvalues[0]), state_full=state)


def overlap_magnitude(left: np.ndarray, right: np.ndarray) -> float:
    left_n = _normalized(left)
    right_n = _normalized(right)
    return float(abs(np.vdot(left_n, right_n)))
