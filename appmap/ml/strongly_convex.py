"""SGD variant for lambda-strongly convex functions.

This module implements a simple, dependency-light version of the SGD
algorithm described for strongly convex objectives (see
`appmap/BOOSTERS_THEOREMS.md` for theorem statements and sketches).

The implementation expects vectors as lists or tuples (or numpy arrays).
It is intentionally small and pure-Python to avoid adding heavy dependencies.
"""
from typing import Callable, Sequence, Optional, Iterable
import random


def _vec_add(a, b):
    return [x + y for x, y in zip(a, b)]


def _vec_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def _vec_scale(a, s: float):
    return [s * x for x in a]


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _norm_sq(a):
    return _dot(a, a)


def sgd_strongly_convex(
    grad_oracle: Callable[[Sequence[float]], Sequence[float]],
    w0: Sequence[float],
    lam: float,
    T: int,
    projection: Optional[Callable[[Sequence[float]], Sequence[float]]] = None,
    seed: Optional[int] = None,
):
    """Run stochastic gradient descent for a lambda-strongly convex f.

    Args:
        grad_oracle: callable(w) -> stochastic subgradient at w (sequence of floats)
        w0: initial point (sequence of floats)
        lam: strong convexity parameter (lambda > 0)
        T: number of iterations
        projection: optional projection onto feasible set H (callable)
        seed: optional RNG seed for reproducibility

    Returns:
        The average iterate \bar{w} (list of floats).

    Notes:
        The algorithm uses step size eta_t = 1/(lam * t) and returns the
        average of the iterates, which enjoys the fast convergence bound
        described in Theorem 14.11 for strongly convex objectives.
    """
    if seed is not None:
        random.seed(seed)

    w = list(w0)
    dim = len(w)
    avg = [0.0] * dim

    for t in range(1, T + 1):
        eta = 1.0 / (lam * t)
        v = grad_oracle(w)
        w_half = _vec_sub(w, _vec_scale(v, eta))
        if projection is not None:
            w = list(projection(w_half))
        else:
            w = w_half
        for i in range(dim):
            avg[i] += w[i]

    return [x / T for x in avg]


def _quadratic_grad_factory(mu: float, noise_std: float = 0.0):
    """Return a stochastic gradient function for f(w) = (mu/2)||w||^2.

    The true gradient is mu * w. This factory adds zero-mean Gaussian noise
    with standard deviation `noise_std` to each coordinate to simulate
    stochastic gradients.
    """

    def grad(w: Sequence[float]):
        return [mu * x + (random.gauss(0, noise_std) if noise_std > 0.0 else 0.0) for x in w]

    return grad


if __name__ == "__main__":
    # Simple demo: minimize f(w) = (mu/2)||w||^2. Optimal solution is w*=0.
    mu = 1.0
    dim = 3
    w0 = [1.0] * dim
    T = 1000
    grad = _quadratic_grad_factory(mu, noise_std=0.1)
    w_bar = sgd_strongly_convex(grad, w0, lam=mu, T=T, seed=42)
    print("average iterate:", w_bar)
    print("norm^2:", _norm_sq(w_bar))
