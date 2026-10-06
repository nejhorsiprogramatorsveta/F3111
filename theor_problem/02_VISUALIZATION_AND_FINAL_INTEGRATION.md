# Visualization, Classical Thermal Ising Model, and Final Integration Specification

Read these files first:

```text
00_MASTER_PROJECT_SPEC.md
01_QUANTUM_ENGINE_AND_ANALYSIS.md
```

Do not rewrite or replace a validated numerical quantum engine simply to simplify plotting.

This stage consumes the quantum data produced by the previous stage and constructs the complete visual submission.

---

# 1. Overall Presentation

Create one coherent notebook, application, or interactive display containing two clearly separated sections:

```text
A. Quantum Ising chain — zero temperature
B. Thermal Ising animation — classical 2D system
```

The user must be able to understand immediately that these are different models.

Use explicit labels.

Recommended top-level headings:

```text
Quantum Ising chain: transverse-field crossover
```

and

```text
Thermal Ising animation
```

Do not label the classical animation as a simulation of quantum time evolution.

---

# 2. Quantum Control

Provide a field slider

```text
g
```

covering approximately

```text
0.1 <= g <= 3.0
```

The slider controls the quantum results only.

If the numerical data are defined on a discrete grid, snap to the nearest computed field value unless a scientifically appropriate interpolation has been intentionally implemented.

Display the actual selected/computed value of `g`.

Do not imply more numerical precision than exists in the data.

---

# 3. Quantum System-Size Control

The order-parameter curves must contain all requested system sizes:

```text
N = 6
N = 8
N = 10
N = 18
```

For state-specific visual panels such as:

```text
measurement strips
correlation heatmap
magnetization probability distribution
```

use one selected `N`.

A system-size selector may be provided.

If interactive performance or memory makes multiple state-vector datasets impractical, use one clearly identified default visualization size while retaining the multi-size curves.

Prefer a size large enough to display useful physics but small enough to remain interactive.

Do not hide which `N` is currently being shown.

---

# 4. Quantum Panel 1 — Measurement Strips

Display several independent simultaneous measurements in the `z` basis.

Each row contains exactly `N` cells.

Use two visually distinct colors for

```text
spin up
spin down
```

Optional arrows are acceptable but not necessary.

Label the panel with wording equivalent to:

```text
Possible measurement outcomes
```

Do not label the strips:

```text
the quantum state
```

or

```text
spin trajectory
```

because they are neither.

Sampling procedure:

```text
sample basis state b with probability |psi_b(g)|^2
```

Each displayed row must be an independent draw.

Expected behavior:

At weak field, sampled rows should often be strongly aligned.

At strong field, mixed `z` outcomes become common.

This occurs even though the strong-field state is increasingly polarized along `x`.

Provide a refresh mechanism if useful.

Changing the slider may also regenerate the displayed samples.

---

# 5. Quantum Panel 2 — Correlation Heatmap

Display

```text
G_ij = <sigma_z[i] sigma_z[j]>
```

as an `N x N` heatmap.

Mandatory requirements:

```text
fixed color limits = [-1, +1]
```

Do not independently normalize the color range for every field value.

Include:

```text
color bar
site labels or readable site indices
clear panel title
selected N
selected g
```

The diagonal will remain equal to `1`.

The scientifically important change is the weakening of long-range off-diagonal correlations with increasing `g`.

---

# 6. Quantum Panel 3 — Exact Magnetization Distribution

Display the exact distribution

```text
p_g(m)
```

as a bar chart.

Use the probabilities computed from the complete quantum state.

Do not use a histogram of the few measurement strips.

Required horizontal axis:

```text
-1 <= m <= +1
```

Use fixed horizontal limits so distributions can be directly compared.

Prefer a fixed probability-axis limit across selected representative snapshots where practical.

Expected visual evolution:

Weak field:

```text
weight near opposite ordered magnetizations
```

Strong field:

```text
distribution concentrated more strongly near zero
```

For finite even-parity states the distribution should remain symmetric:

```text
p(m) = p(-m)
```

up to numerical error.

---

# 7. Quantum Panel 4 — Order and Polarization Curves

Plot

```text
m_rms(g)
```

and

```text
m_x(g)
```

over the full field range.

Include curves for all requested system sizes.

Make the distinction between the two observables visually clear.

There are several acceptable layouts:

### Option A

One axes for `m_rms` and one axes for `m_x`.

### Option B

Both observables on the same axes using different line styles and a clear legend.

Choose whichever is more readable.

Do not use unrelated dual y-axis scaling that obscures comparison.

At the current slider value, display a moving marker on the relevant curve or curves.

The user should be able to see the current value of:

```text
g
N
m_rms
m_x
```

---

# 8. Optional Transition Indicator Plot

If layout permits, include or make accessible a plot of

```text
chi_x(g) = dm_x/dg
```

for the requested sizes.

Mark

```text
g_star(N)
```

for each `N`.

This plot is useful for explaining how the finite-size crossover sharpens.

If it would overload the main four-panel display, include it in a separate analysis section below the required dashboard.

Do not replace any required panel with this optional plot.

---

# 9. Quantum Snapshot Frames

Produce representative outputs at approximately:

```text
g = 0.2
g = 1.0
g = 3.0
```

Use the closest actual precomputed field values if those exact values are not present.

Each representative frame must display or accompany:

```text
g
N
m_rms
m_x
G_far
```

Use consistent visual scales so the three cases can be directly compared.

Especially maintain:

```text
heatmap range [-1, 1]
magnetization x-axis [-1, 1]
```

Avoid automatic axis changes that exaggerate small differences.

---

# 10. Reversibility of Quantum Slider

The quantum results are equilibrium calculations.

Therefore:

```text
g = 0.2 -> g = 3 -> g = 0.2
```

must recover the same deterministic observables.

The only differences allowed are newly drawn random measurement strips.

The UI must not progressively mutate a quantum spin configuration while the slider moves.

No quantum Markov process is part of this assignment.

---

# 11. Classical Thermal Ising Model

Implement an independent classical model on a square lattice.

Required lattice:

```text
L = 32
```

so the total number of spins is

```text
L^2 = 1024
```

Each spin is

```text
s[x,y] = +1 or -1
```

Use periodic boundaries in both dimensions.

No external magnetic field.

Set

```text
J = 1
k_B = 1
```

The classical energy is

```text
E =
    -sum over nearest-neighbour pairs s_i s_j
```

Each bond should conceptually be counted once when computing total energy, although total energy is not necessarily required for every animation frame.

---

# 12. Thermal Update Algorithm

Use a standard local Monte Carlo update.

Either of the following is acceptable:

```text
Metropolis
heat bath
```

Do not invent a nonphysical rule merely to make domains grow faster.

---

# 13. Heat-Bath Implementation

If using heat bath, for a selected site calculate

```text
neighbor_sum =
    s_up + s_down + s_left + s_right
```

Then the probability of setting the selected spin to `+1` is

```text
P(+1 | neighbours) =
    1 / [1 + exp(-2 * neighbor_sum / T)]
```

because

```text
J = 1
```

Then choose

```text
s_i = +1
```

with that probability and

```text
s_i = -1
```

otherwise.

Select sites randomly.

---

# 14. Metropolis Implementation

If using Metropolis instead, for a proposed spin flip calculate

```text
Delta_E =
    2 * s_i * neighbor_sum
```

for `J = 1`.

Accept if

```text
Delta_E <= 0
```

otherwise accept with probability

```text
exp(-Delta_E / T)
```

Both algorithms are acceptable.

Choose one and use it consistently.

---

# 15. Updates per Animation Frame

Perform enough local spin updates between displayed frames that domain growth is visible.

One natural unit is a Monte Carlo sweep:

```text
L^2
```

attempted/local updates.

Several sweeps may be executed per displayed frame depending on performance.

Expose an animation speed control that changes how many updates or sweeps occur per frame and/or the frame interval.

Do not claim the frame number represents calibrated physical time.

---

# 16. Thermal State Persistence

The most important interaction rule is:

Changing temperature must not randomize the lattice.

If the user changes:

```text
T = 4
```

to

```text
T = 1.5
```

the simulation continues from exactly the existing spin configuration.

If the user later raises the temperature back to

```text
T = 4
```

continue from the ordered configuration that formed at low temperature.

Only the explicit reset control should randomize the lattice.

---

# 17. Thermal Initialization

On initial startup or reset:

```text
choose every spin randomly as +/-1
```

with approximately equal probability.

Provide reproducibility support using a random seed where practical.

The main animation may remain stochastic.

---

# 18. Thermal Temperature Slider

Provide a separate slider:

```text
0.5 <= T <= 5.0
```

This slider controls only the classical thermal simulation.

Clearly mark the exact infinite square-lattice critical temperature

```text
T_c =
    2 / ln(1 + sqrt(2))
    approx 2.269185...
```

This marking may be:

```text
a slider annotation
a vertical marker on a companion scale
a displayed textual reference
```

The animation must not force an instantaneous switch at `T_c`.

The lattice should evolve naturally according to stochastic local updates.

---

# 19. Thermal Display

Display the complete

```text
32 x 32
```

spin lattice.

Use two fixed colors for the two spin orientations.

Do not automatically change colors with temperature.

Include a clear title:

```text
Thermal Ising animation
```

Display at least:

```text
current T
instantaneous |m|
```

where

```text
m =
    (1/L^2) sum_i s_i
```

and therefore

```text
|m| =
    absolute value of the lattice-average spin
```

---

# 20. Thermal Controls

Provide:

```text
Play
Pause
Reset
Temperature slider
Animation speed control
```

Expected behavior:

### Play

Repeatedly perform thermal updates and refresh the display.

### Pause

Stop automatic updates while preserving the current lattice.

### Reset

Replace the current lattice by a new random configuration.

### Temperature

Change the update probabilities but preserve the current lattice.

### Speed

Adjust the visual/update rate.

---

# 21. Required Thermal Demonstration

Ensure the program supports this exact workflow:

```text
1. Reset/randomize.
2. Set T approximately 4.
3. Allow high-temperature disorder to be visible.
4. Lower T to approximately 1.5.
5. Continue updating.
6. Observe ordered domains grow.
7. Wait long enough for substantial ordering.
8. Raise T back to approximately 4.
9. Continue updating.
10. Observe domains breaking apart and disorder returning.
```

Global alignment may take time.

Especially near the critical temperature, large competing domains can persist.

Do not artificially overwrite the lattice with a fully ordered state.

---

# 22. Thermal Snapshots

Capture at least:

```text
one low-temperature snapshot
one high-temperature snapshot
```

Prefer snapshots taken from the running simulation rather than manually fabricated arrays.

Include:

```text
T
|m|
```

with each image or its caption.

---

# 23. Layout Recommendation

A practical notebook/application layout is:

```text
=====================================================
Quantum Ising Chain
=====================================================

Controls:
[N selector] [g slider]

[measurement strips]     [correlation heatmap]

[p(m) bar chart]         [m_rms / m_x curves]

Current values:
g = ...
N = ...
m_rms = ...
m_x = ...
G_far = ...

=====================================================
Finite-Size Transition Analysis
=====================================================

chi_x curves
g_star table
grid-refinement results

=====================================================
Thermal Ising Animation
=====================================================

T slider
play / pause / reset / speed

[32 x 32 spin lattice]

T = ...
|m| = ...
Tc = 2.269...

=====================================================
Validation and Numerical Checks
=====================================================

benchmark tables
residuals
dense-vs-sparse check
Hellmann-Feynman check
=====================================================
```

The exact visual arrangement may differ.

Readability and scientific clarity are more important than decorative design.

---

# 24. Final Results Table

Produce a compact summary table containing at least:

```text
N
g_star_coarse
g_star_refined
difference
peak chi_x
```

If available, include representative values near:

```text
g = 0.2
g = 1
g = 3
```

for

```text
m_rms
m_x
G_far
```

Avoid overstating numerical precision.

---

# 25. Final Physical Explanation

The completed notebook/application should contain a concise written explanation of the observed physics.

It must communicate the following ideas accurately.

## Ferromagnetic side

At weak transverse field, the interaction term dominates and distant spins remain strongly correlated in the `z` direction.

The finite-system ground state respects the global spin-flip symmetry and therefore does not choose either ferromagnetic direction.

Consequently,

```text
<Mz> = 0
```

does not mean the system lacks ferromagnetic order.

The order is instead visible through quantities such as:

```text
m_rms
G_far
p_g(m)
```

---

## Paramagnetic side

At strong transverse field, spins tend to align with the applied `x` field.

Therefore:

```text
m_x -> 1
```

Longitudinal correlations weaken.

A simultaneous measurement in the `z` basis can still produce up and down outcomes because an `x`-polarized spin is a quantum superposition of the two `z` states.

This is not a thermal random mixture.

---

## Finite-size crossover

For finite `N`, the change around

```text
g approximately 1
```

is smooth.

As `N` increases, the crossover becomes sharper.

The peak of

```text
chi_x = dm_x/dg
```

defines a useful finite-size pseudo-critical field

```text
g_star(N)
```

but it is not itself the exact thermodynamic critical point.

The known infinite-chain critical value is

```text
g_c = 1
```

for the chosen normalization.

---

## Classical animation

The classical two-dimensional model illustrates a conceptually different transition.

Its control parameter is temperature, not a quantum field.

At low temperature thermal fluctuations are weak and aligned domains grow.

At high temperature thermal fluctuations destroy long-range order.

Its exact infinite-lattice critical temperature is approximately

```text
T_c = 2.269
```

The animation illustrates stochastic relaxation and domain evolution.

It does not represent time evolution of the quantum chain.

---

# 26. Performance Expectations

Interactive updates should remain responsive.

Do not diagonalize the `N = 18` quantum Hamiltonian during every slider event.

Quantum data must be precomputed or cached.

The classical lattice, in contrast, should continue computing local updates while playing.

Keep these computational models separate.

---

# 27. Reproducibility

Provide one central random-number generator or controlled seeds where practical.

Quantum observables are deterministic.

Only the following elements should be stochastic:

```text
sampled quantum measurement strips
classical thermal updates
classical initial/random-reset lattice
```

A fixed demonstration seed is acceptable for snapshots.

The live visualization may use nondeterministic entropy if desired.

---

# 28. Final Verification Checklist

Before declaring the project finished, explicitly verify all of the following.

## Quantum computation

- required `N` values computed;
- required `g` range covered;
- refined region near `g = 1`;
- even parity correctly enforced;
- ground-state residual small;
- observables calculated;
- probability distributions normalized;
- correlation matrices correct;
- dense-vs-sparse validation passed;
- benchmark limits passed;
- Hellmann-Feynman relation checked.

## Quantum UI

- measurement strips update;
- exact probability chart update;
- heatmap update;
- curves update;
- moving marker works;
- slider works in both directions;
- heatmap limits remain `[-1,1]`;
- measurement x-axis remains `[-1,1]`;
- current `N` and `g` displayed;
- representative frames created.

## Transition analysis

- `chi_x` computed;
- `g_star` found for every requested size;
- refined local grid used;
- coarse/refined differences reported;
- no unsupported extrapolation presented.

## Classical UI

- lattice size `32 x 32`;
- periodic boundaries;
- correct thermal update;
- `T` range `0.5` to `5`;
- `T_c` marked;
- play works;
- pause works;
- reset works;
- speed control works;
- changing `T` preserves lattice;
- `|m|` displayed;
- low-temperature ordering visible;
- high-temperature disorder visible;
- low/high snapshots created.

## Scientific presentation

- quantum `g` and classical `T` never conflated;
- quantum samples are described as measurement outcomes;
- classical frames are not described as quantum dynamics;
- finite-size transition is not falsely described as discontinuous;
- pseudo-critical fields are not falsely called exact critical points.

---

# 29. Codex Instructions for Final Stage

Before modifying visualization code:

1. Read all three specification files completely.
2. Inspect the existing numerical API.
3. Run the quantum tests.
4. Reuse the validated API rather than duplicating physics calculations in UI callbacks.
5. Build the required quantum visualization.
6. Test slider reversibility.
7. Build the classical thermal simulator independently.
8. Verify that changing `T` preserves the thermal lattice.
9. Integrate both sections.
10. Generate required snapshots.
11. Run the entire validation suite again.
12. Run the final application/notebook end to end.

After completion, provide:

```text
files changed
tests executed
test results
representative numerical outputs
g_star table
location of generated snapshots
instructions to launch the final notebook/application
known limitations, if any
```

Do not claim completion merely because the UI renders.

Completion requires both numerical correctness and working interaction.