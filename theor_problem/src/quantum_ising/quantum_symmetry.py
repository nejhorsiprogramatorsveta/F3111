"""Global spin-flip parity reduction and state reconstruction."""

from __future__ import annotations

import numpy as np

from .quantum_basis import ComputationalBasis


def reconstruct_full_state(state_even: np.ndarray, basis: ComputationalBasis) -> np.ndarray:
    if state_even.shape != (basis.even_dim,):
        raise ValueError("state_even has incompatible shape")
    state_full = np.zeros(basis.dim, dtype=np.complex128)
    amplitudes = np.asarray(state_even, dtype=np.complex128) / np.sqrt(2.0)
    reps = basis.representatives
    comps = basis.complements[basis.representatives_mask]
    state_full[reps] = amplitudes
    state_full[comps] = amplitudes
    return state_full


def parity_expectation(state_full: np.ndarray, basis: ComputationalBasis) -> complex:
    return complex(np.vdot(state_full, state_full[basis.complements]))


def even_basis_orthonormality_error(basis: ComputationalBasis) -> float:
    projection = basis.even_projection_matrix()
    overlap = (projection.T.conj() @ projection).toarray()
    return float(np.max(np.abs(overlap - np.eye(basis.even_dim))))


def phase_align(state: np.ndarray) -> np.ndarray:
    aligned = np.asarray(state, dtype=np.complex128).copy()
    nonzero = np.flatnonzero(np.abs(aligned) > 1e-14)
    if nonzero.size == 0:
        return aligned
    phase = np.exp(-1j * np.angle(aligned[nonzero[0]]))
    aligned *= phase
    return aligned
