# Quantum Ising Phase Transition — Master Project Specification

## 1. Purpose

Build a complete computational visualization of the transverse-field quantum Ising model and a separate thermal Ising animation.

The submission must demonstrate two physically different phenomena:

1. A zero-temperature quantum phase transition in a one-dimensional transverse-field Ising chain.
2. A temperature-driven ordering transition in a classical two-dimensional Ising model.

These two systems must appear in the same overall submission, but they must remain conceptually and computationally distinct.

Do not identify the quantum transverse field `g` with the classical temperature `T`.

---

# 2. Main Quantum Model

Consider `N` spin-1/2 sites on a periodic one-dimensional ring.

Use

```text
H(g) = -J sum_j sigma_z[j] sigma_z[j+1]
       -J g sum_j sigma_x[j]
```

with periodic boundary conditions

```text
sigma[N+1] = sigma[1]
```

and set

```text
J = 1
```

throughout the main quantum calculation.

The transverse field is therefore controlled by the dimensionless parameter

```text
g = h / J
```

The infinite-chain critical point for this normalization is

```text
g_c = 1
```

The finite chains used here do not exhibit an exact singular transition. They exhibit a smooth crossover that becomes increasingly sharp as `N` grows.

Do not manufacture a discontinuity for finite `N`.

---

# 3. Required System Sizes

Compute results for

```text
N = 6
N = 8
N = 10
N = 18
```

The implementation should not unnecessarily hard-code these values. Wherever reasonable, functions should work for arbitrary manageable `N`.

---

# 4. Required Field Range

Sweep the transverse field approximately over

```text
0.1 <= g <= 3.0
```

Use a denser grid around the expected transition.

At minimum include dense sampling over approximately

```text
0.7 <= g <= 1.3
```

An initial spacing of approximately

```text
delta_g = 0.02
```

is acceptable near the transition, but the grid must later be refined when locating the finite-size susceptibility peak.

The quantum data should be precomputed before interactive visualization.

The interactive slider should select or interpolate already-computed equilibrium results rather than solving a large eigenproblem on every UI update.

---

# 5. Required Quantum Observables

For every selected `N` and `g`, calculate the ground-state energy

```text
E0(g)
```

and the ground state

```text
|psi0(g)>
```

Then calculate the following quantities.

## 5.1 RMS longitudinal magnetization

Define

```text
Mz = (1/N) sum_j sigma_z[j]
```

and compute

```text
m_rms(g) = sqrt(<Mz^2>)
```

This quantity is used because the finite-size symmetric ground state has zero mean longitudinal magnetization even in the ferromagnetic regime.

Do not use

```text
<Mz>
```

as the order parameter for the finite symmetric ground state.

---

## 5.2 Transverse magnetization

Compute

```text
m_x(g) = (1/N) sum_j <sigma_x[j]>
```

At large transverse field this should approach `1`.

---

## 5.3 Correlation matrix

Compute

```text
G_ij(g) = <sigma_z[i] sigma_z[j]>
```

for all site pairs.

The diagonal elements satisfy

```text
G_ii = 1
```

and are therefore not by themselves evidence of ordering.

Long-distance off-diagonal correlations are the important diagnostic.

---

## 5.4 Magnetization probability distribution

Calculate the exact probability of measuring a normalized longitudinal magnetization

```text
m = (1/N) sum_j z_j
```

where each measured spin has

```text
z_j = +1 or -1
```

The exact probability is

```text
p_g(m) =
    sum over basis states b having magnetization m
    of |psi0_b(g)|^2
```

Do not estimate this distribution from a small collection of sampled measurements.

The bar chart must use the exact quantum probabilities.

---

## 5.5 Long-distance correlation

For even `N`, calculate the diametrically opposite correlation

```text
G_far(g) =
    (1/N) sum_j G[j, j + N/2]
```

with the site index interpreted periodically.

---

# 6. Required Finite-Size Transition Indicator

Compute

```text
chi_x(g) = d m_x / d g
```

Numerically estimate this derivative from the precomputed data.

For a locally uniform grid one may use

```text
chi_x(g) approx
    [m_x(g + delta_g) - m_x(g - delta_g)]
    / (2 delta_g)
```

For a nonuniform grid use a derivative formula that correctly accounts for nonuniform spacing.

For each `N`:

1. Find the maximum of `chi_x(g)` near `g = 1`.
2. Call its field position

```text
g_star(N)
```

3. Refine the field grid around that peak.
4. Recalculate the peak.
5. Report how much the estimated `g_star(N)` changed after refinement.

Interpret `g_star(N)` only as a finite-size transition indicator.

Do not call it an exact critical point.

Do not estimate the critical point by looking for `m_rms = 0`, because for a finite chain `m_rms` does not vanish exactly.

Do not perform an unsupported thermodynamic extrapolation from only these few small system sizes.

---

# 7. Physical Interpretation

The project should clearly demonstrate the following.

## Weak field

For

```text
g << 1
```

the interaction dominates.

The state belongs to the ordered regime.

Long-distance `z` correlations are strong.

The exact finite-system parity-symmetric ground state has approximately two dominant measurement sectors corresponding to mostly/all-up and mostly/all-down configurations.

Its expectation value

```text
<Mz>
```

is nevertheless zero because of the global spin-flip symmetry.

---

## Strong field

For

```text
g >> 1
```

the state approaches

```text
|+x> tensor product over N sites
```

where

```text
|+x> = (|up> + |down>) / sqrt(2)
```

This is a quantum paramagnet.

It is not a classical random thermal mixture.

It is strongly polarized along `x`, while simultaneous `z` measurements produce many mixed configurations.

For finite `N`,

```text
m_rms -> 1 / sqrt(N)
```

rather than exactly zero.

---

# 8. Required Quantum Visualization

Create one interactive quantum section containing four linked panels.

All four panels share the same quantum field control `g`.

The panels are:

1. Spin measurement strips.
2. Correlation heatmap.
3. Exact longitudinal magnetization probability distribution.
4. Order/polarization curves.

Changing `g` must update all four consistently.

The control must work in both directions.

Moving the slider from weak field to strong field and back must reproduce the same equilibrium observables.

Only newly sampled measurement strips may change because they are random measurements drawn from the same underlying probability distribution.

Do not display the measurement strips as real-time quantum trajectories.

---

# 9. Required Classical Thermal Animation

Create a separate classical two-dimensional Ising simulation.

Use a

```text
32 x 32
```

square lattice with periodic boundary conditions.

Use classical spins

```text
s_i = +/-1
```

and

```text
E = -J sum_<ij> s_i s_j
```

with

```text
J = 1
k_B = 1
```

and no external field.

Temperature must be independently adjustable over approximately

```text
0.5 <= T <= 5
```

Display the exact infinite-square-lattice critical temperature

```text
T_c = 2 / ln(1 + sqrt(2))
    approx 2.269
```

The simulation may use standard Metropolis or heat-bath local updates.

Unlike the quantum section, this thermal panel is a dynamical visual relaxation process.

The spin configuration must persist while `T` changes.

Only a reset control should replace the lattice with a new random configuration.

---

# 10. Required Thermal Demonstration

The completed application/notebook must allow the following demonstration:

1. Start around

```text
T = 4
```

2. Lower the temperature to approximately

```text
T = 1.5
```

3. Continue updating the same spin lattice.
4. Allow ordered domains to form and grow.
5. Raise the temperature back to approximately

```text
T = 4
```

6. Show the ordered domains breaking up.

Do not force an instantaneous phase switch at `T_c`.

The animation should naturally relax through local stochastic updates.

Frame number is not physical time.

No quantum time evolution is required.

---

# 11. Required Saved Outputs

Save or otherwise produce three representative quantum frames at approximately

```text
g = 0.2
g = 1.0
g = 3.0
```

Use identical plot scales wherever comparisons are intended.

Each frame must display or report:

```text
m_rms
m_x
G_far
```

Also save:

```text
one low-temperature classical snapshot
one high-temperature classical snapshot
```

---

# 12. Numerical Validation

Correctness is more important than visual polish.

The implementation must perform explicit numerical checks.

At minimum verify:

```text
H = H^\dagger
```

```text
<psi0|psi0> = 1
```

```text
<P> approximately 1
```

where `P` is the global spin-flip parity operator.

Calculate the eigenpair residual

```text
||H psi0 - E0 psi0|| / max(1, |E0|)
```

and report it.

A small residual alone does not prove that the selected eigenstate is the ground state, so additional checks are required.

For small `N`, compare the sparse ground-state result against a full dense diagonalization.

Tighten sparse solver tolerances and verify that physical observables remain stable.

Verify

```text
sum_m p_g(m) = 1
```

and

```text
sum_m m^2 p_g(m) = m_rms^2
```

For the even-parity ground state verify

```text
p_g(m) = p_g(-m)
```

to numerical precision.

At multiple field values also verify the independent derivative relation

```text
-(1/NJ) dE0/dg = m_x(g)
```

using finite differences and demonstrate convergence as the derivative spacing is refined.

---

# 13. Required Limiting-Case Tests

## Ferromagnetic benchmark at g = 0

Explicitly test the even ferromagnetic state

```text
|psi_F> =
    (|up up ... up> + |down down ... down>)
    / sqrt(2)
```

Verify

```text
E0 = -J N
m_rms = 1
m_x = 0
G_ij = 1
p(+1) = 1/2
p(-1) = 1/2
```

Also explain why

```text
<Mz> = 0
```

despite perfect ferromagnetic correlations.

---

## Independent-spin benchmark

Perform a separate test using the original Hamiltonian form

```text
H =
    -J sum sigma_z[j] sigma_z[j+1]
    -h sum sigma_x[j]
```

Set

```text
J = 0
h > 0
```

Do not use `g = h/J` in this test because that ratio is undefined when `J = 0`.

Verify

```text
E0 = -h N
m_x = 1
m_rms = N^(-1/2)
G_ij = delta_ij
```

For exactly `k` measured down spins verify

```text
p(m = 1 - 2k/N)
    = 2^(-N) * binomial(N, k)
```

The interacting calculation at `g = 3` should only approach this limit.

Do not artificially force the `g = 3` data to equal the independent-spin result.

---

# 14. Implementation Principles

Use Python unless an existing repository clearly requires another language.

Preferred scientific stack:

```text
numpy
scipy
matplotlib
```

Interactive components may use one appropriate framework such as:

```text
ipywidgets
matplotlib widgets
Plotly
Panel
Dash
Streamlit
```

Choose the smallest framework appropriate to the existing repository and expected submission format.

Avoid introducing unnecessary dependencies.

---

# 15. Recommended Project Architecture

A reasonable architecture is:

```text
src/
    quantum_basis.py
    quantum_hamiltonian.py
    quantum_symmetry.py
    quantum_solver.py
    quantum_observables.py
    data_precompute.py
    transition_analysis.py
    classical_ising.py
    visualization.py

tests/
    test_hamiltonian.py
    test_symmetry.py
    test_limits.py
    test_observables.py
    test_derivative_relation.py

data/
    precomputed/

outputs/
    quantum_frames/
    thermal_snapshots/

main.ipynb
```

This is a recommendation, not an absolute requirement.

Adapt to the existing repository if it already has an established structure.

---

# 16. Coding Requirements

Code must be modular.

Do not put the entire project in one enormous notebook cell or one monolithic script.

Separate:

```text
Hamiltonian construction
symmetry handling
ground-state solution
observables
validation
data generation
classical thermal simulation
visualization
```

Use functions with explicit inputs and outputs.

Document nontrivial physics and numerical choices.

Avoid unnecessary abstractions that obscure the equations.

---

# 17. Performance Requirements

The largest required system has

```text
2^18 = 262144
```

basis states in the full Hilbert space.

Therefore:

- do not construct dense `2^N x 2^N` matrices for large `N`;
- use sparse representations or an appropriate matrix-free method;
- exploit symmetry reduction where specified;
- do not recompute identical basis information repeatedly;
- cache/precompute static arrays where useful.

Dense diagonalization is acceptable only for small validation systems.

---

# 18. Scientific Integrity Requirements

Never alter the physics just to obtain prettier plots.

In particular:

- do not force `m_rms` to zero;
- do not break symmetry unless explicitly performing a separate symmetry-broken experiment;
- do not interpret random measurement samples as the quantum wavefunction;
- do not interpret random samples as real-time quantum spin flips;
- do not rescale heatmap colors independently at every `g`;
- do not confuse classical `T` with quantum `g`;
- do not claim a finite-size pseudo-critical point is the exact critical point;
- do not fabricate a discontinuity around `g = 1`.

---

# 19. Completion Criteria

The project is complete only when all of the following are working:

- sparse quantum Hamiltonian;
- correct periodic bonds;
- even-parity ground-state treatment;
- reconstruction of the full state where required;
- all required observables;
- magnetization distribution;
- long-distance correlation;
- precomputed data over the required field range;
- finite-size susceptibility analysis;
- refined `g_star(N)` estimates;
- numerical validation suite;
- weak-field benchmark;
- independent-spin benchmark;
- interactive four-panel quantum visualization;
- classical `32 x 32` thermal animation;
- independent `g` and `T` controls;
- play/pause/reset/speed controls for thermal animation;
- required quantum snapshots;
- required thermal snapshots;
- final summary of physical findings.

---

# 20. Instructions to Codex

Before implementing any substantial functionality:

1. Read this entire file.
2. Inspect the existing repository.
3. Do not assume the repository is empty.
4. Preserve correct existing work.
5. Identify the smallest coherent architecture consistent with this specification.
6. Run existing tests before modification where possible.
7. Do not begin visualization work before the quantum numerical core is validated.

After reading this file, read the remaining specifications in numerical order.

The later files provide implementation details and override generic architectural suggestions in this file where they are more specific.