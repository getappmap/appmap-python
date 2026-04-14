"""Small examples demonstrating `regex_boost` and `sgd_strongly_convex`.

Run as a script for a quick smoke check.
"""
from appmap import regex_boost
from appmap.ml import sgd_strongly_convex


def demo_regex():
    pat = r"\bword\b"
    s = "this is a word in a sentence"
    m = regex_boost.cached_search(pat, s)
    print("regex found:", bool(m))


def demo_sgd():
    # quadratic objective f(w) = (mu/2)||w||^2, optimum at 0
    mu = 0.5
    w0 = [2.0, -1.0]
    T = 500

    def grad(w):
        return [mu * x for x in w]

    w_avg = sgd_strongly_convex(grad, w0, lam=mu, T=T, seed=0)
    print("sgd avg:", w_avg)


if __name__ == "__main__":
    demo_regex()
    demo_sgd()
