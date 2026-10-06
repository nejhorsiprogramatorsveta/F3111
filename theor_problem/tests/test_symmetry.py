from __future__ import annotations

import numpy as np

from quantum_ising.quantum_basis import ComputationalBasis
from quantum_ising.quantum_hamiltonian import build_even_sector_by_projection, build_even_sector_hamiltonian
from quantum_ising.quantum_symmetry import even_basis_orthonormality_error, parity_expectation, reconstruct_full_state


def test_complement_and_representative_count() -> None:
    basis = ComputationalBasis(6)
    assert basis.complement_state(0b001011) == 0b110100
    assert basis.representatives.size == 2 ** 5


def test_even_basis_projection_is_orthonormal() -> None:
    basis = ComputationalBasis(4)
    assert even_basis_orthonormality_error(basis) < 1e-12


def test_reconstructed_even_state_has_positive_parity() -> None:
    basis = ComputationalBasis(4)
    state_even = np.zeros(basis.even_dim)
    state_even[0] = 1.0
    state_full = reconstruct_full_state(state_even, basis)
    assert np.isclose(np.linalg.norm(state_full), 1.0)
    assert np.isclose(parity_expectation(state_full, basis), 1.0)


def test_direct_even_sector_matches_projection_construction() -> None:
    basis = ComputationalBasis(6)
    direct = np.asarray(build_even_sector_hamiltonian(basis, g=0.9).todense())
    projected = np.asarray(build_even_sector_by_projection(basis, g=0.9).todense())
    assert np.allclose(direct, projected)
