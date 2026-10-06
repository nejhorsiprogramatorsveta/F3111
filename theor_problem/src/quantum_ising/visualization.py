"""Visualization helpers for the quantum and thermal Ising deliverable."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np

from .classical_ising import ClassicalIsingModel, CRITICAL_TEMPERATURE
from .quantum_basis import ComputationalBasis
from .quantum_observables import sample_measurements

SYSTEM_SIZES = [6, 8, 10, 18]
VISUALIZATION_SIZE = 18
SPIN_CMAP = ListedColormap(["#2166ac", "#b2182b"])
THERMAL_CMAP = ListedColormap(["#313695", "#a50026"])
VIRIDIS = plt.get_cmap("viridis")
PLASMA = plt.get_cmap("plasma")


def nearest_index(values: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(values - target)))


def _style_figure() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")


def quantum_dashboard_figure(
    dataset: dict[int, dict[str, np.ndarray]],
    *,
    selected_g: float,
    measurement_seed: int,
    measurement_rows: int = 12,
    visualization_size: int = VISUALIZATION_SIZE,
) -> tuple[Figure, dict[str, float]]:
    _style_figure()
    payload = dataset[visualization_size]
    g_values = payload["g_values"]
    g_index = nearest_index(g_values, selected_g)
    actual_g = float(g_values[g_index])
    basis = ComputationalBasis(visualization_size)
    probabilities = payload["basis_probabilities"][g_index]
    measurements = sample_measurements(
        np.sqrt(probabilities).astype(np.complex128),
        basis,
        num_samples=measurement_rows,
        seed=measurement_seed,
    )

    figure, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    ax_meas, ax_heat, ax_prob, ax_curves = axes.flat

    measurement_image = ((measurements + 1) // 2).astype(int)
    ax_meas.imshow(measurement_image, aspect="auto", cmap=SPIN_CMAP, vmin=0, vmax=1)
    ax_meas.set_title(f"Possible measurement outcomes (N={visualization_size}, g={actual_g:.2f})")
    ax_meas.set_xlabel("Site index")
    ax_meas.set_ylabel("Sample")

    correlations = payload["correlations"][g_index]
    heat = ax_heat.imshow(correlations, cmap="coolwarm", vmin=-1, vmax=1)
    ax_heat.set_title(f"Correlation heatmap G_ij (N={visualization_size}, g={actual_g:.2f})")
    ax_heat.set_xlabel("j")
    ax_heat.set_ylabel("i")
    figure.colorbar(heat, ax=ax_heat, fraction=0.046, pad=0.04)

    magnetization_values = payload["magnetization_values"]
    magnetization_probabilities = payload["magnetization_probabilities"][g_index]
    ax_prob.bar(magnetization_values, magnetization_probabilities, width=1.8 / (visualization_size + 1), color="#4c72b0")
    ax_prob.set_title("Exact longitudinal magnetization distribution")
    ax_prob.set_xlabel("m")
    ax_prob.set_ylabel("p_g(m)")
    ax_prob.set_xlim(-1.0, 1.0)
    ax_prob.set_ylim(0.0, 1.0)

    colors = VIRIDIS(np.linspace(0.15, 0.95, len(SYSTEM_SIZES)))
    for color, size in zip(colors, SYSTEM_SIZES):
        series = dataset[size]
        ax_curves.plot(series["g_values"], series["m_rms"], color=color, linewidth=2)
        ax_curves.plot(series["g_values"], series["m_x"], color=color, linestyle="--", linewidth=2)
        current_index = nearest_index(series["g_values"], actual_g)
        ax_curves.scatter(series["g_values"][current_index], series["m_rms"][current_index], color=color, s=45)
        ax_curves.scatter(series["g_values"][current_index], series["m_x"][current_index], color=color, s=45, marker="s")
    ax_curves.set_title("Order and polarization curves")
    ax_curves.set_xlabel("g")
    ax_curves.set_ylabel("Observable value")
    ax_curves.set_xlim(float(dataset[SYSTEM_SIZES[0]]["g_values"][0]), float(dataset[SYSTEM_SIZES[0]]["g_values"][-1]))
    ax_curves.set_ylim(0.0, 1.05)
    size_handles = [Line2D([0], [0], color=color, lw=2, label=f"N={size}") for color, size in zip(colors, SYSTEM_SIZES)]
    style_handles = [
        Line2D([0], [0], color="black", lw=2, linestyle="-", label=r"$m_{\rm rms}$"),
        Line2D([0], [0], color="black", lw=2, linestyle="--", label=r"$m_x$"),
    ]
    legend_one = ax_curves.legend(handles=size_handles, loc="upper left", title="System size")
    ax_curves.add_artist(legend_one)
    ax_curves.legend(handles=style_handles, loc="lower right", title="Observable")

    summary = {
        "g": actual_g,
        "N": float(visualization_size),
        "m_rms": float(payload["m_rms"][g_index]),
        "m_x": float(payload["m_x"][g_index]),
        "G_far": float(payload["g_far"][g_index]),
    }
    return figure, summary


def transition_analysis_figure(
    dataset: dict[int, dict[str, np.ndarray]],
    transition_rows: list[dict[str, float]],
) -> Figure:
    _style_figure()
    figure, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    colors = PLASMA(np.linspace(0.15, 0.95, len(SYSTEM_SIZES)))
    for color, size, row in zip(colors, SYSTEM_SIZES, transition_rows):
        g_values = dataset[size]["g_values"]
        chi_values = np.gradient(dataset[size]["m_x"], g_values)
        ax.plot(g_values, chi_values, color=color, label=f"N={size}")
        ax.scatter(row["g_star_refined"], row["peak_chi_x"], color=color, s=50)
    ax.axvline(1.0, color="black", linestyle=":", linewidth=1.5, label="g_c = 1")
    ax.set_title(r"Finite-size susceptibility $\chi_x = dm_x/dg$")
    ax.set_xlabel("g")
    ax.set_ylabel(r"$\chi_x$")
    ax.legend(ncol=3)
    return figure


def thermal_lattice_figure(model: ClassicalIsingModel) -> Figure:
    _style_figure()
    figure, ax = plt.subplots(figsize=(6, 6), constrained_layout=True)
    ax.imshow((model.lattice > 0).astype(int), cmap=THERMAL_CMAP, vmin=0, vmax=1, interpolation="nearest")
    ax.set_title(
        f"Thermal Ising animation\nT={model.temperature:.2f}, |m|={model.abs_magnetization():.3f}, Tc={CRITICAL_TEMPERATURE:.3f}"
    )
    ax.set_xticks([])
    ax.set_yticks([])
    return figure


def save_figure(figure: Figure, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)
