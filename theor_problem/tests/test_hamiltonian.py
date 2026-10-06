from __future__ import annotations

import numpy as np

from quantum_ising.quantum_basis import ComputationalBasis
from quantum_ising.quantum_hamiltonian import build_dense_hamiltonian, build_sparse_hamiltonian


def test_sparse_hamiltonian_dimension_and_hermiticity() -> None:
    basis = ComputationalBasis(4)
    hamiltonian = np.asarray(build_sparse_hamiltonian(basis, g=0.7).todense())
    assert hamiltonian.shape == (16, 16)
    assert np.allclose(hamiltonian, hamiltonian.T.conj())


def test_periodic_bond_counting_on_reference_states() -> None:
    basis = ComputationalBasis(4)
    diagonal = basis.interaction_diagonal(coupling=1.0)
    assert diagonal[0] == -4.0
    assert diagonal[0b0101] == 4.0


def test_spin_flip_matrix_elements_are_not_doubled() -> None:
    basis = ComputationalBasis(3)
    hamiltonian = build_dense_hamiltonian(basis, coupling=1.0, h=1.3)
    assert hamiltonian[0b001, 0b000] == -1.3
    assert hamiltonian[0b010, 0b000] == -1.3
    assert hamiltonian[0b100, 0b000] == -1.3
    assert hamiltonian[0b011, 0b000] == 0.0
