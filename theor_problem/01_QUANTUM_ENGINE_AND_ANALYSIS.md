# Quantum Ising Numerical Engine and Analysis Specification

This file defines the implementation of the zero-temperature one-dimensional transverse-field quantum Ising calculation.

Read `00_MASTER_PROJECT_SPEC.md` before this file.

Do not start the interactive visualization until this numerical layer passes its validation tests.

---

# 1. Computational Basis

Represent each `N`-spin `z`-basis configuration by an integer

```text
b = 0, 1, ..., 2^N - 1
```

Use the bit convention

```text
bit j = 0  -> spin up   -> z_j = +1
bit j = 1  -> spin down -> z_j = -1
```

Therefore

```text
z_j(b) = 1 - 2 * bit_j(b)
```

Choose one consistent site-to-bit convention and document it.

The physics is invariant under whether site `0` is stored in the least-significant or most-significant bit, but all routines must use the same convention.

---

# 2. Full Sparse Hamiltonian

For `J = 1`, implement

```text
H(g) =
    -sum_j sigma_z[j] sigma_z[j+1]
    -g sum_j sigma_x[j]
```

with periodic boundaries.

---

## 2.1 Diagonal interaction term

For every basis state `b` calculate

```text
H[b,b] =
    -sum_j z_j(b) z_(j+1)(b)
```

where

```text
j+1
```

wraps periodically.

Count each ring bond exactly once.

For `N` sites there are exactly `N` nearest-neighbour bonds.

---

## 2.2 Off-diagonal transverse-field term

Applying

```text
sigma_x[j]
```

flips bit `j`.

For every basis state `b` and site `j`, define

```text
b_flipped = b XOR (1 << j)
```

Then

```text
H[b_flipped, b] += -g
```

If generating every spin flip from every basis state, the reverse direction will naturally be generated when `b_flipped` itself is later visited.

Do not add an extra matrix transpose afterward.

Doing so would double the off-diagonal field term.

---

## 2.3 Sparse storage

For nontrivial systems construct the Hamiltonian with SciPy sparse matrices.

A COO construction converted to CSR/CSC is acceptable.

For example:

```text
scipy.sparse.coo_matrix
scipy.sparse.csr_matrix
```

Do not construct the full dense Hamiltonian for `N = 18`.

---

# 3. Global Spin-Flip Symmetry

The Hamiltonian commutes with

```text
P = product_j sigma_x[j]
```

which reverses every `z` spin.

In the computational basis it maps

```text
|b> -> |bar(b)>
```

where

```text
bar(b)
```

is the bitwise complement restricted to the lowest `N` bits.

Implement for example

```text
mask = (1 << N) - 1
bar_b = b XOR mask
```

For every basis configuration `b`, exactly one complementary state exists.

---

# 4. Even-Parity Basis

For the finite periodic chain with `g > 0`, use the even-parity ground-state sector.

Construct symmetry-adapted basis states

```text
|b;+> =
    (|b> + |bar(b)>) / sqrt(2)
```

choosing only one representative from every complementary pair.

A simple canonical rule is

```text
b < bar(b)
```

The dimension of this sector is

```text
2^(N-1)
```

for the systems considered here.

---

# 5. Preferred Symmetry Implementation

There are two acceptable implementation strategies.

## Strategy A — explicit projection matrix

Construct a sparse matrix `Q` whose columns are the symmetry-adapted basis vectors.

Each column contains exactly two nonzero values

```text
1 / sqrt(2)
```

located at `b` and `bar(b)`.

Then construct

```text
H_even = Q^\dagger H Q
```

and diagonalize `H_even`.

After obtaining the even-sector eigenvector

```text
psi_even
```

reconstruct the full computational-basis state with

```text
psi_full = Q psi_even
```

This is conceptually straightforward and follows the mathematical specification directly.

---

## Strategy B — direct even-sector construction

A more memory-efficient implementation may construct `H_even` directly in the representative basis without explicitly creating the full `H`.

This is acceptable only if:

1. the mapping is correct;
2. normalization is correct;
3. it produces results matching Strategy A for small test systems;
4. the code remains understandable.

If uncertain, implement Strategy A first and optimize only after obtaining validated results.

---

# 6. Ground-State Solver

For sparse matrices use a solver appropriate for the lowest algebraic eigenvalue, for example:

```text
scipy.sparse.linalg.eigsh
```

with

```text
which="SA"
```

or another explicitly equivalent method.

Do not ask for the eigenvalue closest to zero.

The desired state is the minimum-energy state.

For example:

```text
eigsh(H_even, k=1, which="SA", ...)
```

Return:

```text
E0
psi_even
psi_full
```

Normalize the eigenvector explicitly if useful, even though the eigensolver should already provide a normalized vector.

---

# 7. Phase and Sign

The global sign or phase of an eigenvector is physically irrelevant.

Tests must compare states modulo a global phase/sign when comparing dense and sparse eigenvectors.

Prefer testing physical observables, energy, overlap magnitude, or residuals instead of raw vector equality.

---

# 8. Parity Verification

After reconstructing the full state, explicitly evaluate

```text
<P>
```

The simplest computational-basis expression is

```text
<P> =
    sum_b conjugate(psi[b]) * psi[bar(b)]
```

For the selected ground state this should satisfy approximately

```text
<P> = +1
```

within numerical tolerance.

If it does not, investigate the solver/symmetry implementation.

Do not silently accept a parity-mixed state.

---

# 9. Ground-State Residual

For every tested ground state calculate

```text
residual =
    ||H psi - E0 psi||
    / max(1, |E0|)
```

Use the full or symmetry-sector Hamiltonian consistently.

Store or report representative residual values.

---

# 10. Observable Implementation

Whenever possible, evaluate diagonal `z` observables directly from the basis-state probabilities

```text
prob[b] = |psi[b]|^2
```

This is simpler and faster than constructing large operator matrices.

---

# 11. Longitudinal Magnetization per Basis State

Precompute

```text
m_z_basis[b] =
    (1/N) sum_j z_j(b)
```

for every basis state.

Then

```text
<Mz> =
    sum_b prob[b] * m_z_basis[b]
```

and

```text
<Mz^2> =
    sum_b prob[b] * m_z_basis[b]^2
```

Therefore

```text
m_rms =
    sqrt(sum_b prob[b] * m_z_basis[b]^2)
```

This must agree with the second moment of the exact magnetization probability distribution.

---

# 12. Exact Magnetization Probability Distribution

Possible normalized magnetizations are

```text
m = -1, -1 + 2/N, ..., +1
```

Group the computational-basis probabilities according to their `m_z_basis`.

For numerical robustness, grouping by number of down spins `k` is preferable to comparing floating-point magnetization values.

For

```text
k = 0, 1, ..., N
```

the corresponding magnetization is

```text
m_k = 1 - 2k/N
```

Compute

```text
p[k] =
    sum over states with popcount(b) = k
    of prob[b]
```

Return aligned arrays

```text
m_values
p_values
```

Verify

```text
sum p_values = 1
```

and for the even ground state

```text
p(m) = p(-m)
```

within tolerance.

---

# 13. Correlation Matrix

For every computational basis state define its vector

```text
z(b) = [z_0, z_1, ..., z_(N-1)]
```

Then

```text
G_ij =
    sum_b prob[b] z_i(b) z_j(b)
```

Possible implementations include:

```text
weighted matrix multiplication
vectorized NumPy operations
carefully optimized loops
```

Avoid constructing one giant quantum operator per `(i,j)` pair.

The result must be an

```text
N x N
```

real matrix.

Verify:

```text
G = G^T
```

and

```text
diag(G) = 1
```

within numerical tolerance.

---

# 14. Long-Distance Correlation

For even `N` compute

```text
G_far =
    (1/N) sum_j G[j, (j + N/2) mod N]
```

Because the ground state is translationally invariant in the ideal calculation, these terms should be similar.

The explicit average makes the diagnostic more robust.

---

# 15. Transverse Magnetization

Compute

```text
m_x =
    (1/N) sum_j <sigma_x[j]>
```

without constructing all `sigma_x` matrices.

Because `sigma_x[j]` flips bit `j`,

```text
<sigma_x[j]> =
    sum_b conjugate(psi[b]) * psi[b XOR (1 << j)]
```

For a real-valued Hamiltonian the ground-state eigenvector can generally be represented as real, but implement the formula safely for complex arrays.

The final expectation value should be real up to numerical noise.

Use:

```text
real_if_close
```

or an equivalent explicit real extraction after verifying the imaginary part is negligible.

---

# 16. Hellmann-Feynman Check

The Hamiltonian satisfies

```text
dH/dg = -sum_j sigma_x[j]
```

Therefore

```text
dE0/dg =
    -sum_j <sigma_x[j]>
    = -N m_x
```

for `J = 1`.

Hence

```text
-(1/N) dE0/dg = m_x
```

Verify this numerically at several interior `g` values.

Use a centered finite difference:

```text
dE0/dg approx
    [E0(g + delta) - E0(g - delta)]
    / (2 delta)
```

Repeat with a smaller `delta`.

The derivative-based estimate should approach the directly computed `m_x`.

Do not use a boundary point where centered differencing is impossible unless using an appropriate one-sided formula.

---

# 17. Measurement Sampling

The quantum visualization requires random simultaneous `z` measurements.

These are not Monte Carlo states.

Sample computational basis states directly according to

```text
prob[b] = |psi[b]|^2
```

For example:

```text
rng.choice(number_of_basis_states, p=prob)
```

Convert each sampled basis state into `N` up/down values.

Every displayed row must be an independent sample from the exact ground-state measurement distribution.

Changing `g` changes the probability distribution.

Refreshing the display at fixed `g` may produce new samples without changing any equilibrium observable.

---

# 18. Precomputed Data Structure

Precompute quantum observables before animation.

A recommended in-memory data structure is conceptually:

```text
results[N][g] = {
    "energy": ...,
    "m_rms": ...,
    "m_x": ...,
    "G": ...,
    "G_far": ...,
    "m_values": ...,
    "p_m": ...,
    "probabilities": ...
}
```

However, storing the full probability vector for every `N` and every `g` may consume significant memory, especially for `N = 18`.

Estimate memory before deciding.

Possible approaches:

### Option 1

Store complete probability vectors only for the system size used in the interactive measurement visualization.

Store scalar/compact observables for all other sizes.

### Option 2

Store the ground-state vectors in compressed NumPy format where practical.

### Option 3

Cache only selected fields and recompute states for rare requested snapshot fields.

Use engineering judgement while preserving interactive responsiveness.

---

# 19. Recommended Field Grid

Construct the grid intentionally rather than only using one coarse `linspace`.

For example:

```text
coarse low-field region
0.1 ... 0.68

dense transition region
0.70 ... 1.30 with ~0.02 spacing initially

coarse high-field region
1.32 ... 3.0
```

Avoid duplicate values when merging grid sections.

The exact grid may be improved, but it must provide enough resolution to show the transition region.

---

# 20. Susceptibility Calculation

For every system size compute

```text
chi_x = d m_x / dg
```

If `g` is not perfectly uniform, prefer

```text
numpy.gradient(m_x_values, g_values)
```

or another derivative method that accepts coordinate values.

Do not apply the simple constant-spacing centered-difference formula to a nonuniform grid as though it were uniform.

---

# 21. Locating g_star(N)

For each `N`:

1. Restrict the peak search to a reasonable region around the transition, such as approximately

```text
0.7 <= g <= 1.3
```

2. Find the largest `chi_x`.
3. Record its corresponding `g`.
4. Define this as the coarse

```text
g_star_coarse(N)
```

5. Generate a finer local field grid around the coarse maximum.
6. Recalculate the quantum data needed for `m_x`.
7. Recalculate the derivative.
8. Find

```text
g_star_refined(N)
```

9. Report

```text
delta_g_star =
    g_star_refined - g_star_coarse
```

Do not use interpolation as a substitute for actually checking refinement unless interpolation is clearly described as an additional estimate.

---

# 22. Dense-vs-Sparse Validation

For a small system such as

```text
N = 4
N = 6
```

construct the same Hamiltonian densely.

Use

```text
numpy.linalg.eigh
```

or

```text
scipy.linalg.eigh
```

to obtain the complete eigenspectrum.

Compare the lowest energy against the sparse/even-sector solver.

Check representative observables as well.

Expected agreement should be near machine/numerical solver precision.

---

# 23. g = 0 Ferromagnetic Benchmark

Construct explicitly

```text
psi_F =
    (|00...0> + |11...1>) / sqrt(2)
```

under the chosen bit convention.

For the pure interaction Hamiltonian at

```text
g = 0
```

verify:

```text
E = -N
m_rms = 1
m_x = 0
G_ij = 1
p(m=+1) = 1/2
p(m=-1) = 1/2
```

and

```text
<Mz> = 0
```

Explain in the final results that the last equation follows because the even superposition contains equal weight in the two opposite ferromagnetic orientations.

The state has perfect correlations even though its signed mean magnetization vanishes.

---

# 24. Independent-Spin Benchmark

Create a test path for the original two-parameter Hamiltonian

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

This test must not calculate

```text
g = h/J
```

because `J = 0`.

The exact ground state is

```text
|+x>^N
```

Verify:

```text
E0 = -h N
m_x = 1
m_rms = 1/sqrt(N)
G_ii = 1
G_ij = 0 for i != j
```

Therefore

```text
G_ij = delta_ij
```

The longitudinal magnetization distribution must be binomial.

For `k` down spins,

```text
m = 1 - 2k/N
```

and

```text
p(m) =
    C(N,k) / 2^N
```

Compare the computed exact distribution with this analytic result.

---

# 25. Solver Tolerance Study

At several representative fields, preferably including values such as

```text
g = 0.2
g = 1.0
g = 3.0
```

solve using at least two eigensolver tolerances.

For example:

```text
tol = 1e-9
tol = 1e-11
```

or values appropriate to the solver.

Report the changes in:

```text
E0
m_rms
m_x
G_far
```

The changes should be negligible relative to the precision displayed in the final output.

---

# 26. Data Validation Function

Create one function or validation module capable of checking a computed result.

It should test as applicable:

```text
state normalization
parity
eigenpair residual
probability normalization
p(m) symmetry
second moment identity
G matrix symmetry
G diagonal
Hellmann-Feynman consistency
```

Return structured results rather than only printing strings.

For example:

```text
{
    "norm_error": ...,
    "parity_error": ...,
    "residual": ...,
    "probability_error": ...,
    ...
}
```

This makes the validation reusable in tests and final reports.

---

# 27. Tests

Create actual automated tests.

At minimum include tests for:

## Hamiltonian

- correct dimension;
- Hermiticity;
- periodic bond counting;
- correct spin-flip matrix elements.

## Symmetry

- complement operation;
- correct number of representatives;
- orthonormality of the even basis;
- `P = +1` for reconstructed even states.

## Observables

- normalization of `p(m)`;
- `m_rms^2` equal to second moment of `p(m)`;
- `G_ii = 1`;
- symmetric `G`;
- correct `m_x` for known states.

## Benchmarks

- `g = 0` even ferromagnetic state;
- `J = 0`, `h > 0` independent-spin state.

## Solvers

- sparse vs dense ground-state energy for small systems.

---

# 28. Expected Qualitative Results

Do not hard-code these values, but use them as sanity checks.

At small `g`:

```text
m_rms approximately 1
m_x relatively small
G_far large and positive
p(m) strongly weighted near +/-1
```

Near

```text
g approximately 1
```

the observables change most rapidly.

At large `g`:

```text
m_x approaches 1
m_rms approaches 1/sqrt(N)
off-diagonal G_ij become small
p(m) becomes centered near m = 0
```

Increasing `N` should make the crossover sharper.

---

# 29. Deliverables from This Stage

Before beginning visualization, the repository must contain working code that can:

1. generate the required field grid;
2. solve the ground state for each requested `N`;
3. calculate all observables;
4. save/cache the data;
5. determine coarse and refined `g_star(N)`;
6. run all numerical tests;
7. print or save a compact validation report.

The numerical layer should be usable independently of any UI.

---

# 30. Codex Completion Rules for This Stage

When implementing this specification:

1. Inspect the repository before modifying files.
2. Briefly state the implementation plan.
3. Implement the smallest clean module structure consistent with the existing project.
4. Run unit tests.
5. Run at least one small end-to-end quantum calculation.
6. Do not merely write code without executing it where the environment permits execution.
7. Show actual validation results.
8. Do not claim that `N = 18` is verified unless that calculation actually ran.
9. If performance prevents a requested calculation, identify the exact bottleneck and improve the implementation rather than silently skipping it.
10. Only after the quantum numerical core is validated should work proceed to the visualization specification.