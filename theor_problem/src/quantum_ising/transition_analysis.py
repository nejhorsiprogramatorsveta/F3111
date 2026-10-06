"""Finite-size transverse-susceptibility peak analysis."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .quantum_basis import ComputationalBasis
from .quantum_observables import compute_observables
from .quantum_solver import solve_ground_state


@dataclass
class TransitionEstimate:
    g_values: np.ndarray
    m_x_values: np.ndarray
    chi_x_values: np.ndarray
    g_star_coarse: float
    g_star_refined: float
    delta_g_star: float
    refined_grid: np.ndarray
    refined_chi_x: np.ndarray


def susceptibility(g_values: np.ndarray, m_x_values: np.ndarray) -> np.ndarray:
    return np.gradient(m_x_values, g_values)


def _restricted_peak(g_values: np.ndarray, values: np.ndarray, *, window: tuple[float, float]) -> tuple[int, float]:
    mask = (g_values >= window[0]) & (g_values <= window[1])
    if not np.any(mask):
        raise ValueError("no grid points inside the requested window")
    local_indices = np.flatnonzero(mask)
    peak_local_index = int(np.argmax(values[mask]))
    peak_index = int(local_indices[peak_local_index])
    return peak_index, float(g_values[peak_index])


def refined_field_grid(
    center: float,
    *,
    step: float = 0.005,
    half_width: float = 0.06,
    bounds: tuple[float, float] = (0.1, 3.0),
) -> np.ndarray:
    left = max(bounds[0], center - half_width)
    right = min(bounds[1], center + half_width)
    return np.arange(left, right + 0.5 * step, step)


def analyze_transition(
    num_sites: int,
    coarse_grid: np.ndarray,
    *,
    window: tuple[float, float] = (0.7, 1.3),
    tolerance: float = 1e-10,
) -> TransitionEstimate:
    basis = ComputationalBasis(num_sites)
    previous_state: np.ndarray | None = None
    m_x_values: list[float] = []
    for g in coarse_grid:
        result = solve_ground_state(basis, g=float(g), tolerance=tolerance, initial_state=previous_state)
        previous_state = result.state_even
        observables = compute_observables(result.state_full, basis)
        m_x_values.append(observables.m_x)
    coarse_mx = np.asarray(m_x_values, dtype=np.float64)
    coarse_chi = susceptibility(coarse_grid, coarse_mx)
    _, g_star_coarse = _restricted_peak(coarse_grid, coarse_chi, window=window)

    refined_grid = refined_field_grid(g_star_coarse)
    previous_state = None
    refined_mx_values: list[float] = []
    for g in refined_grid:
        result = solve_ground_state(basis, g=float(g), tolerance=tolerance, initial_state=previous_state)
        previous_state = result.state_even
        observables = compute_observables(result.state_full, basis)
        refined_mx_values.append(observables.m_x)
    refined_mx = np.asarray(refined_mx_values, dtype=np.float64)
    refined_chi = susceptibility(refined_grid, refined_mx)
    _, g_star_refined = _restricted_peak(refined_grid, refined_chi, window=window)

    return TransitionEstimate(
        g_values=coarse_grid,
        m_x_values=coarse_mx,
        chi_x_values=coarse_chi,
        g_star_coarse=g_star_coarse,
        g_star_refined=g_star_refined,
        delta_g_star=g_star_refined - g_star_coarse,
        refined_grid=refined_grid,
        refined_chi_x=refined_chi,
    )
