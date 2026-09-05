"""Recover a willingness-to-pay estimate from binary referendum responses.

Two estimators, deliberately both reported:

* `turnbull_mean` -- nonparametric. Integrates the yes-share curve over the bid
  range. Assumes nothing about the shape of the distribution, but is bounded by
  the highest bid offered, so it understates when the curve has not fallen to
  zero by $750.
* `logit_median` -- fits P(yes) = logistic(a + b * bid) and returns -a/b. Gives
  a value outside the bid range when warranted, at the cost of a parametric
  assumption and a meaningless answer when b >= 0.

Where they disagree, the disagreement is the finding, not a nuisance: a model
whose yes-share never falls has no recoverable WTP inside the design, and that
should be reported rather than papered over with an extrapolation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class WTPEstimate:
    turnbull_mean: float
    logit_median: float | None
    logit_slope: float | None
    n: int
    yes_share_at_max_bid: float
    censored: bool

    @property
    def preferred(self) -> float | None:
        """Logit median unless the curve is degenerate, else the Turnbull mean."""
        if self.logit_median is None:
            return self.turnbull_mean if not self.censored else None
        return self.logit_median


def yes_shares(bids: list[int], votes: list[bool | None]) -> dict[int, tuple[int, int]]:
    """bid -> (yes_count, n) over non-null votes."""
    out: dict[int, tuple[int, int]] = {}
    for bid, vote in zip(bids, votes, strict=True):
        if vote is None:
            continue
        yes, n = out.get(bid, (0, 0))
        out[bid] = (yes + int(vote), n + 1)
    return out


def turnbull_mean(shares: dict[int, tuple[int, int]]) -> float:
    """Trapezoid integral of the yes-share curve from $0 to the highest bid.

    The curve is assumed to start at 1.0 at a price of zero. It is NOT forced to
    be monotone: a non-monotone yes-share curve is itself a coherence violation
    and should stay visible in the estimate rather than being smoothed away.
    """
    if not shares:
        return float("nan")
    xs = [0] + sorted(shares)
    ys = [1.0] + [yes / n for _, (yes, n) in sorted(shares.items())]
    return float(np.trapezoid(ys, xs))


def logit_fit(shares: dict[int, tuple[int, int]], *, max_iter: int = 100) -> tuple[float, float] | None:
    """Newton-Raphson fit of P(yes) = logistic(a + b * bid). None if degenerate."""
    if len(shares) < 2:
        return None
    x = np.array(sorted(shares), dtype=float)
    yes = np.array([shares[int(b)][0] for b in x], dtype=float)
    n = np.array([shares[int(b)][1] for b in x], dtype=float)
    if yes.sum() in (0.0, n.sum()):
        return None  # no variation to fit

    beta = np.array([0.0, 0.0])
    design = np.column_stack([np.ones_like(x), x])
    for _ in range(max_iter):
        eta = design @ beta
        p = 1.0 / (1.0 + np.exp(-eta))
        w = n * p * (1.0 - p)
        if not np.all(np.isfinite(w)) or w.sum() <= 1e-12:
            return None
        gradient = design.T @ (yes - n * p)
        hessian = design.T @ (design * w[:, None])
        try:
            step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError:
            return None
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            break
    else:
        return None
    return float(beta[0]), float(beta[1])


def estimate(bids: list[int], votes: list[bool | None]) -> WTPEstimate:
    shares = yes_shares(bids, votes)
    fit = logit_fit(shares)
    median: float | None = None
    slope: float | None = None
    if fit is not None:
        a, b = fit
        slope = b
        # A non-negative slope means yes-share rises with price: no WTP exists.
        if b < 0:
            median = -a / b
    max_bid = max(shares) if shares else 0
    yes_at_max = (shares[max_bid][0] / shares[max_bid][1]) if shares else float("nan")
    return WTPEstimate(
        turnbull_mean=turnbull_mean(shares),
        logit_median=median,
        logit_slope=slope,
        n=sum(n for _, n in shares.values()),
        yes_share_at_max_bid=yes_at_max,
        censored=bool(shares) and yes_at_max > 0.5,
    )
