from __future__ import annotations

from pathlib import Path

import numpy as np
import streamlit as st

from quantum_ising.classical_ising import CRITICAL_TEMPERATURE, ClassicalIsingModel
from quantum_ising.data_precompute import ensure_precomputed_dataset
from quantum_ising.reporting import OUTPUT_ROOT, PRECOMPUTE_DIR, generate_transition_rows, run_validation_summary, save_transition_table, save_validation_summary
from quantum_ising.visualization import SYSTEM_SIZES, VISUALIZATION_SIZE, quantum_dashboard_figure, thermal_lattice_figure, transition_analysis_figure

st.set_page_config(page_title="Quantum and Thermal Ising Project", layout="wide")

ROOT = Path(__file__).resolve().parent
MAIN_PLOT_WIDTH = 820
SECONDARY_PLOT_WIDTH = 700
PLOT_COLUMN_RATIOS = [1, 5, 1]


@st.cache_resource(show_spinner=True)
def load_dataset() -> dict[int, dict[str, np.ndarray]]:
    return ensure_precomputed_dataset(
        ROOT / PRECOMPUTE_DIR,
        system_sizes=SYSTEM_SIZES,
        include_probabilities_for={VISUALIZATION_SIZE},
        force=False,
    )


@st.cache_resource(show_spinner=True)
def load_transition_rows() -> list[dict[str, float]]:
    rows = generate_transition_rows(load_dataset())
    save_transition_table(rows, ROOT / OUTPUT_ROOT / "transition_table.csv")
    return rows


@st.cache_resource(show_spinner=True)
def load_validation_summary() -> dict[str, object]:
    summary = run_validation_summary()
    save_validation_summary(summary, ROOT / OUTPUT_ROOT / "validation_summary.json")
    return summary


def centered_plot(figure, *, width: int) -> None:
    _, center_col, _ = st.columns(PLOT_COLUMN_RATIOS)
    with center_col:
        st.pyplot(figure, clear_figure=True, width=width)


def initialize_state() -> None:
    if "measurement_seed" not in st.session_state:
        st.session_state.measurement_seed = 2026
    if "thermal_model" not in st.session_state:
        st.session_state.thermal_model = ClassicalIsingModel(size=32, temperature=4.0, seed=2026)
    if "thermal_playing" not in st.session_state:
        st.session_state.thermal_playing = False
    if "thermal_speed" not in st.session_state:
        st.session_state.thermal_speed = 4
    if "thermal_frame" not in st.session_state:
        st.session_state.thermal_frame = 0
    if "thermal_resets" not in st.session_state:
        st.session_state.thermal_resets = 0


initialize_state()
dataset = load_dataset()
transition_rows = load_transition_rows()
validation_summary = load_validation_summary()

st.title("Quantum Ising chain: transverse-field crossover")
st.caption("Quantum observables are loaded from the validated precomputed numerical engine; the UI does not recompute the large eigenproblem on slider updates.")

quantum_payload = dataset[VISUALIZATION_SIZE]
g_values = quantum_payload["g_values"]
selected_g = st.slider(
    "Transverse field g",
    min_value=float(g_values[0]),
    max_value=float(g_values[-1]),
    value=1.0,
    step=0.01,
    help="The dashboard snaps to the nearest precomputed equilibrium field value.",
)
refresh_col, info_col = st.columns([1, 3])
with refresh_col:
    if st.button("Refresh measurement strips"):
        st.session_state.measurement_seed += 1
with info_col:
    st.write(f"State-specific panels use fixed visualization size N = {VISUALIZATION_SIZE}.")

quantum_figure, quantum_summary = quantum_dashboard_figure(
    dataset,
    selected_g=selected_g,
    measurement_seed=st.session_state.measurement_seed,
    visualization_size=VISUALIZATION_SIZE,
)
centered_plot(quantum_figure, width=MAIN_PLOT_WIDTH)

metric_cols = st.columns(5)
metric_cols[0].metric("Computed g", f"{quantum_summary['g']:.2f}")
metric_cols[1].metric("Selected N", f"{int(quantum_summary['N'])}")
metric_cols[2].metric("m_rms", f"{quantum_summary['m_rms']:.4f}")
metric_cols[3].metric("m_x", f"{quantum_summary['m_x']:.4f}")
metric_cols[4].metric("G_far", f"{quantum_summary['G_far']:.4f}")

st.markdown(
    "The measurement strips are independent simultaneous $z$-basis samples drawn from the exact precomputed basis probabilities. The bar chart shows the exact $p_g(m)$ distribution, not a sample histogram."
)

st.header("Finite-size transition analysis")
transition_figure = transition_analysis_figure(dataset, transition_rows)
centered_plot(transition_figure, width=SECONDARY_PLOT_WIDTH)
st.table(transition_rows)
st.caption("The refined g* values are finite-size pseudo-critical indicators, not exact thermodynamic critical points.")

@st.fragment(run_every=0.2)
def render_thermal_animation() -> None:
    st.header("Thermal Ising animation")
    st.caption("This classical 32x32 model is independent from the quantum calculation. Changing temperature preserves the existing lattice; only reset randomizes it.")
    model: ClassicalIsingModel = st.session_state.thermal_model

    thermal_temperature = st.slider(
        "Temperature T",
        min_value=0.5,
        max_value=5.0,
        value=float(model.temperature),
        step=0.05,
        help=f"Critical temperature reference: Tc = {CRITICAL_TEMPERATURE:.3f}",
    )
    model.set_temperature(thermal_temperature)
    st.session_state.thermal_speed = st.slider("Sweeps per frame", min_value=1, max_value=25, value=int(st.session_state.thermal_speed))

    play_col, pause_col, step_col, reset_col = st.columns(4)
    if play_col.button("Play"):
        st.session_state.thermal_playing = True
    if pause_col.button("Pause"):
        st.session_state.thermal_playing = False
    if step_col.button("Step once"):
        model.run(sweeps=int(st.session_state.thermal_speed))
        st.session_state.thermal_frame += 1
    if reset_col.button("Reset"):
        st.session_state.thermal_resets += 1
        model.reset(seed=2026 + st.session_state.thermal_resets)

    if st.session_state.thermal_playing:
        model.run(sweeps=int(st.session_state.thermal_speed))
        st.session_state.thermal_frame += 1

    thermal_figure = thermal_lattice_figure(model)
    centered_plot(thermal_figure, width=SECONDARY_PLOT_WIDTH)

    thermal_metrics = st.columns(5)
    thermal_metrics[0].metric("T", f"{model.temperature:.2f}")
    thermal_metrics[1].metric("|m|", f"{model.abs_magnetization():.4f}")
    thermal_metrics[2].metric("Tc", f"{CRITICAL_TEMPERATURE:.3f}")
    thermal_metrics[3].metric("Frames", f"{st.session_state.thermal_frame}")
    thermal_metrics[4].metric("Status", "Playing" if st.session_state.thermal_playing else "Paused")


render_thermal_animation()

st.header("Validation and numerical checks")
st.json(validation_summary, expanded=False)

st.header("Physical interpretation")
st.markdown(
    "- Weak transverse field preserves strong long-distance $z$ correlations even though $\\langle M_z \\rangle = 0$ in the finite even-parity ground state.\n"
    "- Strong transverse field drives $m_x \\to 1$ while $z$-basis measurements remain mixed because the state is a quantum superposition, not a thermal mixture.\n"
    "- The crossover sharpens with increasing $N$, and the peak of $\\chi_x$ defines a finite-size $g_\\star(N)$ near the known infinite-chain critical value $g_c = 1$.\n"
    "- The lower panel is a separate classical stochastic relaxation problem controlled by temperature $T$, not by the quantum field $g$.\n"
    "- SIX SEVEEN"
)

