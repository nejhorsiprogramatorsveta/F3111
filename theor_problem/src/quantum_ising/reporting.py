"""Output generation and final integration helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from .classical_ising import ClassicalIsingModel
from .data_precompute import compute_quantum_point, ensure_precomputed_dataset, generate_field_grid
from .quantum_basis import ComputationalBasis
from .transition_analysis import analyze_transition
from .validation import (
    dense_sparse_comparison,
    g0_ferromagnetic_benchmark,
    hellmann_feynman_check,
    independent_spin_benchmark,
    solver_tolerance_study,
)
from .visualization import SYSTEM_SIZES, VISUALIZATION_SIZE, quantum_dashboard_figure, save_figure, thermal_lattice_figure


OUTPUT_ROOT = Path("outputs")
PRECOMPUTE_DIR = Path("data/precomputed")


def generate_transition_rows(dataset: dict[int, dict[str, np.ndarray]]) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    grid = generate_field_grid()
    for num_sites in SYSTEM_SIZES:
        estimate = analyze_transition(num_sites, grid)
        payload = dataset[num_sites]
        refined_peak_index = int(np.argmax(estimate.refined_chi_x))
        rows.append(
            {
                "N": float(num_sites),
                "g_star_coarse": float(estimate.g_star_coarse),
                "g_star_refined": float(estimate.g_star_refined),
                "difference": float(estimate.delta_g_star),
                "peak_chi_x": float(estimate.refined_chi_x[refined_peak_index]),
                "m_rms_g0p2": float(payload["m_rms"][np.argmin(np.abs(payload["g_values"] - 0.2))]),
                "m_x_g1p0": float(payload["m_x"][np.argmin(np.abs(payload["g_values"] - 1.0))]),
                "g_far_g3p0": float(payload["g_far"][np.argmin(np.abs(payload["g_values"] - 3.0))]),
            }
        )
    return rows


def save_transition_table(rows: list[dict[str, float]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_validation_summary() -> dict[str, object]:
    grid = generate_field_grid()
    validation_points = {}
    for num_sites in SYSTEM_SIZES:
        point_reports = {}
        for g in (0.2, 1.0, 3.0):
            point = compute_quantum_point(
                basis=ComputationalBasis(num_sites),
                g=g,
                include_probabilities=False,
            )
            point_reports[str(g)] = {
                "energy": point.energy,
                "m_rms": point.observables.m_rms,
                "m_x": point.observables.m_x,
                "g_far": point.observables.g_far,
                "norm_error": point.validation.norm_error,
                "parity": float(np.real(point.validation.parity_expectation)),
                "residual": point.validation.residual,
                "probability_error": point.validation.probability_error,
                "second_moment_error": point.validation.second_moment_error,
            }
        validation_points[str(num_sites)] = point_reports
    summary = {
        "dense_sparse_N6_g1.0": dense_sparse_comparison(6, g=1.0),
        "g0_benchmark_N6": {k: v for k, v in g0_ferromagnetic_benchmark(6).items() if k != "correlation_matrix" and k != "probabilities"},
        "independent_spin_N6_h1.2": {k: v for k, v in independent_spin_benchmark(6, h=1.2).items() if k not in {"correlation_matrix", "distribution", "expected_distribution"}},
        "hellmann_feynman_N6_g1.0": hellmann_feynman_check(6, g=1.0, delta=0.005),
        "solver_tolerance_N6": solver_tolerance_study(6, g_values=[0.2, 1.0, 3.0]),
        "pointwise_validation": validation_points,
        "field_grid_size": len(grid),
    }
    return summary


def save_validation_summary(summary: dict[str, object], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def generate_quantum_snapshots(dataset: dict[int, dict[str, np.ndarray]], *, measurement_seed: int = 2026) -> list[str]:
    outputs: list[str] = []
    for selected_g in (0.2, 1.0, 3.0):
        figure, summary = quantum_dashboard_figure(
            dataset,
            selected_g=selected_g,
            measurement_seed=measurement_seed + int(selected_g * 100),
            visualization_size=VISUALIZATION_SIZE,
        )
        file_path = OUTPUT_ROOT / "quantum_frames" / f"quantum_g_{summary['g']:.2f}.png"
        save_figure(figure, file_path)
        outputs.append(str(file_path))
    return outputs


def generate_thermal_snapshots(*, seed: int = 2026) -> list[str]:
    model = ClassicalIsingModel(size=32, temperature=4.0, seed=seed)
    model.run(sweeps=60)
    high_path = OUTPUT_ROOT / "thermal_snapshots" / "thermal_high_T.png"
    save_figure(thermal_lattice_figure(model), high_path)

    model.set_temperature(1.5)
    model.run(sweeps=220)
    low_path = OUTPUT_ROOT / "thermal_snapshots" / "thermal_low_T.png"
    save_figure(thermal_lattice_figure(model), low_path)
    return [str(low_path), str(high_path)]


def generate_all_outputs(force_precompute: bool = True) -> dict[str, object]:
    dataset = ensure_precomputed_dataset(
        PRECOMPUTE_DIR,
        system_sizes=SYSTEM_SIZES,
        include_probabilities_for={VISUALIZATION_SIZE},
        force=force_precompute,
    )
    transition_rows = generate_transition_rows(dataset)
    save_transition_table(transition_rows, OUTPUT_ROOT / "transition_table.csv")
    validation_summary = run_validation_summary()
    save_validation_summary(validation_summary, OUTPUT_ROOT / "validation_summary.json")
    quantum_files = generate_quantum_snapshots(dataset)
    thermal_files = generate_thermal_snapshots()
    return {
        "transition_rows": transition_rows,
        "validation_summary": validation_summary,
        "quantum_files": quantum_files,
        "thermal_files": thermal_files,
    }
