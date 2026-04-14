# Theorems and Notes for Appmap Boosters

This document collects concise theorem statements and short proof sketches
for the `regex_boost` and `ml.strongly_convex` boosters included in this
repository. It is intended as lightweight, local documentation for
engineers and experimental users.

---

## Regex Boost: caching and backend speedup

Theorem 1 (Amortized compile cost).
Let C be the cost to compile a pattern and M the cost to execute a single
match with a compiled pattern. Suppose a pattern p is used k >= 1 times.
Using a caching layer that compiles p at most once yields total cost
at most C + k·M, vs k·C + k·M without caching. Hence the amortized per-use
compile overhead is reduced from C to C/k.

Proof sketch: The cache guarantees a single compilation on first use; all
subsequent uses access the compiled object with O(1) lookup, therefore
total cost is C + k·M.

Corollary (Memory/time tradeoff). Caching up to N distinct patterns reduces
recompilation if the working set of frequently-used patterns is <= N;
evicting patterns increases miss rate. Choose cache size based on memory
budget and empirical pattern reuse.

Theorem 2 (Backend advantage for complex features).
If an alternative regex engine implements an algorithmic improvement for a
class of patterns P (for example, atomic groups, possessive quantifiers,
or JIT compilation), then there exists a constant α < 1 such that for all
p ∈ P and typical inputs the engine's match cost M' ≤ α·M, yielding
end-to-end speedups when matching dominates runtime.

Remark: This is an empirical/theoretical observation rather than a single
universal bound; results depend on pattern structure and the specific
engine's optimizations.

---

## Strongly Convex SGD (summary of key statements)

Definition (λ-strong convexity).
A function f is λ-strongly convex on a convex set H if for all u,w∈H and
any subgradient g∈∂f(w):

    f(u) ≥ f(w) + ⟨g, u−w⟩ + (λ/2) ||u−w||^2.

Claim (generalized monotonicity).
If f is λ-strongly convex then for every w,u and v ∈ ∂f(w) we have

    ⟨w−u, v⟩ ≥ f(w) − f(u) + (λ/2) ||w−u||^2.

Theorem (Stochastic Gradient Descent for λ-strongly convex functions).
Assume f is λ-strongly convex and that the stochastic subgradients vt
satisfy E[||vt||^2] ≤ ρ^2. Let w* = argmin f. Run projected SGD with
step sizes η_t = 1/(λ t) and output the average iterate w̄ = (1/T)
∑_{t=1}^T w^(t). Then

    E[f(w̄)] − f(w*) ≤ (ρ^2 / (2 λ T)) (1 + log T).

Proof sketch:
- Use strong convexity to relate ⟨w^(t) − w*, ∇(t)⟩ to f(w^(t)) − f(w*)
  plus a quadratic term (Claim above).
- Use the projection property and textbook algebra to bound
  ⟨w^(t) − w*, ∇(t)⟩ by a telescoping sum of squared norms plus
  η_t^2 E[||v_t||^2]/2.
- Summing over t and choosing η_t = 1/(λ t) yields a bound with
  harmonic sums that produce the log(T) term.

Remark: Variants of the algorithm that average a suffix of iterates (e.g.
the last T/2) can eliminate the log(T) factor and achieve O(1/(λ T)). See
Rakhlin, Shamir & Sridharan (2012) for such refinements.

---

References and further reading
- Standard convex optimization texts and lecture notes (e.g. Shalev-Shwartz
  & Ben-David, Bubeck) cover strong convexity and SGD convergence proofs.
- The code in `appmap/ml/strongly_convex.py` implements the simple averaged
  SGD variant whose convergence is summarized above.
