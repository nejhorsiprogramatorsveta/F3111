"""Sparse transverse-field Ising Hamiltonian construction."""

from __future__ import annotations

import numpy as np
from scipy import sparse

from .quantum_basis import ComputationalBasis


def resolve_transverse_field(*, coupling: float, g: float | None, h: float | None) -> float:
    if h is not None:
        return float(h)
    if g is None:
        raise ValueError("provide either g or h")
    return float(coupling) * float(g)


def build_sparse_hamiltonian(
    basis: ComputationalBasis,
    *,
    coupling: float = 1.0,
    g: float | None = None,
    h: float | None = None,
    fmt: str = "csr",
) -> sparse.spmatrix:
    transverse = resolve_transverse_field(coupling=coupling, g=g, h=h)
    dim = basis.dim
    num_sites = basis.num_sites
    nnz = dim * (num_sites + 1)

    rows = np.empty(nnz, dtype=np.int32)
    cols = np.empty(nnz, dtype=np.int32)
    data = np.empty(nnz, dtype=np.float64)

    states = basis.states.astype(np.int32, copy=False)
    diagonal = basis.interaction_diagonal(coupling)
    rows[:dim] = states
    cols[:dim] = states
    data[:dim] = diagonal

    for site in range(num_sites):
        start = dim * (site + 1)
        stop = start + dim
        rows[start:stop] = np.bitwise_xor(states, np.int32(1 << site))
        cols[start:stop] = states
        data[start:stop] = -transverse

    matrix = sparse.coo_matrix((data, (rows, cols)), shape=(dim, dim))
    return matrix.asformat(fmt)


def build_dense_hamiltonian(
    basis: ComputationalBasis,
    *,
    coupling: float = 1.0,
    g: float | None = None,
    h: float | None = None,
) -> np.ndarray:
    transverse = resolve_transverse_field(coupling=coupling, g=g, h=h)
    dense = np.diag(basis.interaction_diagonal(coupling))
    states = basis.states.astype(np.int64, copy=False)
    for site in range(basis.num_sites):
        dense[np.bitwise_xor(states, 1 << site), states] += -transverse
    return dense


def build_even_sector_hamiltonian(
    basis: ComputationalBasis,
    *,
    coupling: float = 1.0,
    g: float | None = None,
    h: float | None = None,
    fmt: str = "csr",
) -> sparse.spmatrix:
    transverse = resolve_transverse_field(coupling=coupling, g=g, h=h)
    even_dim = basis.even_dim
    num_sites = basis.num_sites
    nnz = even_dim * (num_sites + 1)

    rows = np.empty(nnz, dtype=np.int32)
    cols = np.empty(nnz, dtype=np.int32)
    data = np.empty(nnz, dtype=np.float64)

    rep_indices = np.arange(even_dim, dtype=np.int32)
    representatives = basis.representatives.astype(np.int32, copy=False)

    diagonal = basis.interaction_diagonal(coupling)[basis.representatives_mask]
    rows[:even_dim] = rep_indices
    cols[:even_dim] = rep_indices
    data[:even_dim] = diagonal

    for site in range(num_sites):
        start = even_dim * (site + 1)
        stop = start + even_dim
        rows[start:stop] = basis.representative_index_of_state[np.bitwise_xor(representatives, np.int32(1 << site))]
        cols[start:stop] = rep_indices
        data[start:stop] = -transverse

    matrix = sparse.coo_matrix((data, (rows, cols)), shape=(even_dim, even_dim))
    return matrix.asformat(fmt)


def build_even_sector_by_projection(
    basis: ComputationalBasis,
    *,
    coupling: float = 1.0,
    g: float | None = None,
    h: float | None = None,
) -> sparse.csr_matrix:
    projection = basis.even_projection_matrix()
    full_hamiltonian = build_sparse_hamiltonian(basis, coupling=coupling, g=g, h=h, fmt="csr")
    return (projection.T.conj() @ full_hamiltonian @ projection).tocsr()
