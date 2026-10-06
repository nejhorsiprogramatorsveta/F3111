"""Basis-state indexing and cached spin-sector metadata.

Site ``j`` is stored in bit ``j`` of the computational-basis integer,
so site 0 is the least-significant bit.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import numpy as np
from scipy import sparse


@dataclass(frozen=True)
class ComputationalBasis:
    """Cached computational-basis metadata for an ``N``-spin chain."""

    num_sites: int

    def __post_init__(self) -> None:
        if self.num_sites <= 0:
            raise ValueError("num_sites must be positive")

    @property
    def dim(self) -> int:
        return 1 << self.num_sites

    @property
    def even_dim(self) -> int:
        return 1 << (self.num_sites - 1)

    @property
    def mask(self) -> int:
        return self.dim - 1

    @cached_property
    def states(self) -> np.ndarray:
        return np.arange(self.dim, dtype=np.uint32)

    @cached_property
    def complements(self) -> np.ndarray:
        return np.bitwise_xor(self.states, np.uint32(self.mask))

    @cached_property
    def representatives_mask(self) -> np.ndarray:
        return self.states < self.complements

    @cached_property
    def representatives(self) -> np.ndarray:
        return self.states[self.representatives_mask]

    @cached_property
    def representative_index_of_state(self) -> np.ndarray:
        mapping = np.empty(self.dim, dtype=np.int32)
        mapping.fill(-1)
        rep_indices = np.arange(self.even_dim, dtype=np.int32)
        reps = self.representatives
        comps = self.complements[self.representatives_mask]
        mapping[reps] = rep_indices
        mapping[comps] = rep_indices
        return mapping

    @cached_property
    def popcounts(self) -> np.ndarray:
        return np.bitwise_count(self.states).astype(np.int16, copy=False)

    @cached_property
    def magnetization_basis(self) -> np.ndarray:
        return 1.0 - 2.0 * self.popcounts.astype(np.float64) / self.num_sites

    @cached_property
    def z_values(self) -> np.ndarray:
        bit_positions = np.arange(self.num_sites, dtype=np.uint32)
        bits = (self.states[:, None] >> bit_positions) & 1
        return (1 - 2 * bits).astype(np.int8, copy=False)

    def complement_state(self, state: int) -> int:
        return int(state) ^ self.mask

    def flip_state(self, state: int, site: int) -> int:
        if site < 0 or site >= self.num_sites:
            raise IndexError("site out of range")
        return int(state) ^ (1 << site)

    def flipped_states(self, site: int) -> np.ndarray:
        return np.bitwise_xor(self.states, np.uint32(1 << site))

    def interaction_diagonal(self, coupling: float = 1.0) -> np.ndarray:
        bonds = self.z_values * np.roll(self.z_values, shift=-1, axis=1)
        return -float(coupling) * bonds.sum(axis=1, dtype=np.int16).astype(np.float64)

    def even_projection_matrix(self) -> sparse.csr_matrix:
        reps = self.representatives.astype(np.int32, copy=False)
        comps = self.complements[self.representatives_mask].astype(np.int32, copy=False)
        cols = np.repeat(np.arange(self.even_dim, dtype=np.int32), 2)
        rows = np.empty(2 * self.even_dim, dtype=np.int32)
        rows[0::2] = reps
        rows[1::2] = comps
        data = np.full(2 * self.even_dim, 1.0 / np.sqrt(2.0), dtype=np.float64)
        return sparse.csr_matrix(sparse.coo_matrix((data, (rows, cols)), shape=(self.dim, self.even_dim)))
