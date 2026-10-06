"""Persistent 2D classical Ising lattice and local thermal updates."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

CRITICAL_TEMPERATURE = 2.0 / np.log(1.0 + np.sqrt(2.0))


@dataclass
class ClassicalIsingModel:
    """32x32 thermal Ising model with periodic boundaries and Metropolis updates."""

    size: int = 32
    temperature: float = 4.0
    seed: int | None = None
    lattice: np.ndarray = field(init=False)
    rng: np.random.Generator = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.size <= 0:
            raise ValueError("size must be positive")
        self.rng = np.random.default_rng(self.seed)
        self.lattice = self._random_lattice()

    def _random_lattice(self) -> np.ndarray:
        return self.rng.choice(np.array([-1, 1], dtype=np.int8), size=(self.size, self.size))

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.lattice = self._random_lattice()

    def set_temperature(self, temperature: float) -> None:
        if temperature <= 0:
            raise ValueError("temperature must be positive")
        self.temperature = float(temperature)

    def magnetization(self) -> float:
        return float(np.mean(self.lattice))

    def abs_magnetization(self) -> float:
        return float(abs(self.magnetization()))

    def neighbor_sum(self, row: int, col: int) -> int:
        spins = self.lattice
        return int(
            spins[(row - 1) % self.size, col]
            + spins[(row + 1) % self.size, col]
            + spins[row, (col - 1) % self.size]
            + spins[row, (col + 1) % self.size]
        )

    def local_energy_change(self, row: int, col: int) -> int:
        return int(2 * self.lattice[row, col] * self.neighbor_sum(row, col))

    def metropolis_update(self) -> None:
        row = int(self.rng.integers(self.size))
        col = int(self.rng.integers(self.size))
        delta_energy = self.local_energy_change(row, col)
        if delta_energy <= 0 or self.rng.random() < np.exp(-delta_energy / self.temperature):
            self.lattice[row, col] *= -1

    def sweep(self, updates: int | None = None) -> None:
        attempts = self.size * self.size if updates is None else int(updates)
        for _ in range(attempts):
            self.metropolis_update()

    def run(self, sweeps: int = 1) -> None:
        for _ in range(int(sweeps)):
            self.sweep()

    def total_energy(self) -> float:
        spins = self.lattice
        horizontal = spins * np.roll(spins, shift=-1, axis=1)
        vertical = spins * np.roll(spins, shift=-1, axis=0)
        return float(-(horizontal.sum() + vertical.sum()))
