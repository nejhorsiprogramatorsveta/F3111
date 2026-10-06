from __future__ import annotations

import numpy as np

from quantum_ising.classical_ising import ClassicalIsingModel


def test_temperature_change_preserves_lattice_and_reset_changes_it() -> None:
    model = ClassicalIsingModel(size=8, temperature=4.0, seed=123)
    original = model.lattice.copy()
    model.set_temperature(1.5)
    assert np.array_equal(model.lattice, original)
    model.reset(seed=456)
    assert model.lattice.shape == (8, 8)
    assert not np.array_equal(model.lattice, original)


def test_metropolis_updates_preserve_spin_values_and_periodic_energy() -> None:
    model = ClassicalIsingModel(size=6, temperature=2.5, seed=5)
    model.run(sweeps=3)
    assert set(np.unique(model.lattice)).issubset({-1, 1})

    ordered = ClassicalIsingModel(size=4, temperature=1.0, seed=1)
    ordered.lattice[:] = 1
    assert np.isclose(ordered.total_energy(), -32.0)
