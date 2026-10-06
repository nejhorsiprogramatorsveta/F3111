"""Field-grid generation, precomputation, and persistent result storage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .quantum_basis import ComputationalBasis
from .quantum_observables import ObservableSet, compute_observables
from .quantum_solver import GroundStateResult, solve_ground_state
from .validation import ValidationReport, validate_result


@dataclass
class QuantumPointResult:
    energy: float
    state_result: GroundStateResult
    observables: ObservableSet
    validation: ValidationReport


def generate_field_grid(
    *,
    low_start: float = 0.1,
    low_stop: float = 0.68,
    low_step: float = 0.08,
    dense_start: float = 0.70,
    dense_stop: float = 1.30,
    dense_step: float = 0.02,
    high_start: float = 1.32,
    high_stop: float = 3.0,
    high_step: float = 0.08,
    anchor_points: tuple[float, ...] = (0.2, 1.0, 3.0),
) -> np.ndarray:
    low = np.arange(low_start, low_stop + 0.5 * low_step, low_step)
    dense = np.arange(dense_start, dense_stop + 0.5 * dense_step, dense_step)
    high = np.arange(high_start, high_stop + 0.5 * high_step, high_step)
    anchors = np.asarray(anchor_points, dtype=np.float64)
    return np.unique(np.round(np.concatenate([low, dense, high, anchors]), 12))


def compute_quantum_point(
    basis: ComputationalBasis,
    *,
    g: float,
    coupling: float = 1.0,
    tolerance: float = 1e-10,
    include_probabilities: bool = False,
    initial_state: np.ndarray | None = None,
) -> QuantumPointResult:
    state_result = solve_ground_state(
        basis,
        coupling=coupling,
        g=g,
        tolerance=tolerance,
        initial_state=initial_state,
    )
    observables = compute_observables(
        state_result.state_full,
        basis,
        include_basis_probabilities=include_probabilities,
    )
    validation = validate_result(basis, state_result, observables, coupling=coupling, g=g)
    return QuantumPointResult(
        energy=state_result.energy,
        state_result=state_result,
        observables=observables,
        validation=validation,
    )


def precompute_quantum_dataset(
    system_sizes: list[int],
    g_values: np.ndarray,
    *,
    include_probabilities_for: set[int] | None = None,
    tolerance: float = 1e-10,
) -> dict[int, dict[str, np.ndarray]]:
    include_probabilities_for = include_probabilities_for or set()
    dataset: dict[int, dict[str, np.ndarray]] = {}
    for num_sites in system_sizes:
        basis = ComputationalBasis(num_sites)
        energies: list[float] = []
        m_rms_values: list[float] = []
        m_x_values: list[float] = []
        g_far_values: list[float] = []
        correlations: list[np.ndarray] = []
        distributions: list[np.ndarray] = []
        norms: list[float] = []
        residuals: list[float] = []
        parities: list[float] = []
        probability_vectors: list[np.ndarray] = []
        previous_even_state: np.ndarray | None = None

        for g in g_values:
            point = compute_quantum_point(
                basis,
                g=float(g),
                tolerance=tolerance,
                include_probabilities=num_sites in include_probabilities_for,
                initial_state=previous_even_state,
            )
            previous_even_state = point.state_result.state_even
            energies.append(point.energy)
            m_rms_values.append(point.observables.m_rms)
            m_x_values.append(point.observables.m_x)
            g_far_values.append(np.nan if point.observables.g_far is None else point.observables.g_far)
            correlations.append(point.observables.correlation_matrix)
            distributions.append(point.observables.magnetization_probabilities)
            norms.append(point.validation.norm_error)
            residuals.append(point.validation.residual)
            parities.append(float(np.real(point.validation.parity_expectation)))
            if point.observables.basis_probabilities is not None:
                probability_vectors.append(point.observables.basis_probabilities)

        result = {
            "g_values": np.asarray(g_values, dtype=np.float64),
            "energies": np.asarray(energies, dtype=np.float64),
            "m_rms": np.asarray(m_rms_values, dtype=np.float64),
            "m_x": np.asarray(m_x_values, dtype=np.float64),
            "g_far": np.asarray(g_far_values, dtype=np.float64),
            "correlations": np.asarray(correlations, dtype=np.float64),
            "magnetization_values": 1.0 - 2.0 * np.arange(num_sites + 1, dtype=np.float64) / num_sites,
            "magnetization_probabilities": np.asarray(distributions, dtype=np.float64),
            "norm_errors": np.asarray(norms, dtype=np.float64),
            "residuals": np.asarray(residuals, dtype=np.float64),
            "parity_expectations": np.asarray(parities, dtype=np.float64),
        }
        if probability_vectors:
            result["basis_probabilities"] = np.asarray(probability_vectors, dtype=np.float64)
        dataset[num_sites] = result
    return dataset


def save_precomputed_dataset(dataset: dict[int, dict[str, np.ndarray]], directory: str | Path) -> None:
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    for num_sites, payload in dataset.items():
        np.savez_compressed(str(output_dir / f"quantum_precompute_N{num_sites}.npz"), **payload)  # pyright: ignore[reportArgumentType]


def load_precomputed_dataset(directory: str | Path, *, system_sizes: list[int]) -> dict[int, dict[str, np.ndarray]]:
    input_dir = Path(directory)
    dataset: dict[int, dict[str, np.ndarray]] = {}
    for num_sites in system_sizes:
        with np.load(input_dir / f"quantum_precompute_N{num_sites}.npz", allow_pickle=False) as payload:
            dataset[num_sites] = {key: payload[key] for key in payload.files}
    return dataset


def ensure_precomputed_dataset(
    directory: str | Path,
    *,
    system_sizes: list[int],
    include_probabilities_for: set[int] | None = None,
    tolerance: float = 1e-10,
    force: bool = False,
) -> dict[int, dict[str, np.ndarray]]:
    include_probabilities_for = include_probabilities_for or set()
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    g_values = generate_field_grid()
    missing: list[int] = []
    for num_sites in system_sizes:
        file_path = output_dir / f"quantum_precompute_N{num_sites}.npz"
        if force or not file_path.exists():
            missing.append(num_sites)
            continue
        with np.load(file_path, allow_pickle=False) as payload:
            has_probabilities = "basis_probabilities" in payload.files
            required_probabilities = num_sites in include_probabilities_for
            if required_probabilities and not has_probabilities:
                missing.append(num_sites)
                continue
            if not np.array_equal(payload["g_values"], g_values):
                missing.append(num_sites)
    if missing:
        computed = precompute_quantum_dataset(
            missing,
            g_values,
            include_probabilities_for=include_probabilities_for,
            tolerance=tolerance,
        )
        save_precomputed_dataset(computed, output_dir)
    return load_precomputed_dataset(output_dir, system_sizes=system_sizes)
