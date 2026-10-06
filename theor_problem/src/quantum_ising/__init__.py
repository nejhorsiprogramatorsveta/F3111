"""Numerical core for the quantum and classical Ising project."""

from .classical_ising import CRITICAL_TEMPERATURE, ClassicalIsingModel
from .data_precompute import compute_quantum_point, ensure_precomputed_dataset, generate_field_grid, load_precomputed_dataset, precompute_quantum_dataset, save_precomputed_dataset
from .quantum_basis import ComputationalBasis
from .quantum_hamiltonian import build_dense_hamiltonian, build_even_sector_by_projection, build_even_sector_hamiltonian, build_sparse_hamiltonian
from .quantum_observables import ObservableSet, compute_observables, sample_measurements
from .quantum_solver import GroundStateResult, solve_dense_ground_state, solve_ground_state
from .reporting import generate_all_outputs, generate_transition_rows, run_validation_summary
from .transition_analysis import TransitionEstimate, analyze_transition, susceptibility
from .validation import (
    ValidationReport,
    dense_sparse_comparison,
    g0_ferromagnetic_benchmark,
    hellmann_feynman_check,
    independent_spin_benchmark,
    solver_tolerance_study,
    validate_result,
)
from .visualization import SYSTEM_SIZES, VISUALIZATION_SIZE, quantum_dashboard_figure, thermal_lattice_figure, transition_analysis_figure
