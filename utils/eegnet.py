"""Dependency-free NumPy EEGNet for the rung-4 raw-waveform load decoder.

This is a faithful, compact implementation of EEGNet (Lawhern et al., 2018,
"EEGNet: a compact convolutional neural network for EEG-based brain-computer
interfaces", J. Neural Eng. 15(5):056013, https://doi.org/10.1088/1741-2552/aace8c)
written in pure NumPy with hand-derived backpropagation. It is hand-rolled for the
same reason ``utils/riemann.py`` is: the project's compute environment cannot host a
deep-learning framework (the C: drive has < 4 GB free, far below a Torch install), and
the Dandelion efficiency standard favours the smallest sufficient solution. The network
here is tiny (~2k parameters), so a NumPy implementation trains in minutes on CPU and
adds zero dependencies.

The architecture follows EEGNet-F1/D/F2 exactly, scaled to this dataset's 8-channel /
200 Hz / 3 s maintenance window:

    input  (N, 1, C, T)
    -> temporal conv      (F1 filters, kernel (1, kt), 'same' over time)   + BN
    -> depthwise spatial  (kernel (C, 1), depth_multiplier D, groups=F1)   + BN + ELU
       -> avg-pool time (factor p1) -> dropout
    -> separable conv     (depthwise (1, kt2) + pointwise (1, 1) -> F2)     + BN + ELU
       -> avg-pool time (factor p2) -> dropout
    -> flatten -> dense (2) -> softmax

Correctness discipline: every gradient is hand-derived, and :func:`gradient_check`
finite-differences the full loss against every parameter. The rung-4 driver asserts the
check passes (max relative error < 1e-4) before any LOSO training, so the negative
result the rung is meant to complete rests on a verified implementation -- the same bar
the Riemannian rung met with its Frechet-mean residual check.

All arrays are float64 for gradient-check accuracy; the dataset is small enough that the
extra precision costs little and removes a class of numerical-mismatch bugs.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# --------------------------------------------------------------------------- #
# Low-level ops: grouped 2-D convolution (forward + backward) via im2col.
# --------------------------------------------------------------------------- #
def _pad_width(x: np.ndarray, kw: int, same: bool) -> tuple[np.ndarray, int, int]:
    """Zero-pad the last axis (time) for 'same' convolution; no-op when ``same`` is False."""
    if not same or kw == 1:
        return x, 0, 0
    total = kw - 1
    left = total // 2
    right = total - left
    xp = np.pad(x, ((0, 0), (0, 0), (0, 0), (left, right)))
    return xp, left, right


def conv2d_forward(x: np.ndarray, W: np.ndarray, groups: int, same_time: bool):
    """Grouped 2-D convolution. Height (channel axis) is always 'valid'; width (time)
    is 'same' or 'valid'.

    Args:
        x: input (N, Cin, H, Wd).
        W: weights (Cout, Cin // groups, kh, kw).
        groups: number of channel groups (1 = dense, Cin = depthwise).
        same_time: pad the time axis so Wout == Wd.

    Returns:
        (y, cache) with y of shape (N, Cout, Hout, Wout).
    """
    N, Cin, H, Wd = x.shape
    Cout, Cing, kh, kw = W.shape
    assert Cin % groups == 0 and Cout % groups == 0 and Cing == Cin // groups
    Coutg = Cout // groups
    xp, pad_l, _ = _pad_width(x, kw, same_time)
    Wp = xp.shape[3]
    Hout = H - kh + 1
    Wout = Wp - kw + 1
    cols_per_group = []
    y = np.empty((N, Cout, Hout, Wout), dtype=x.dtype)
    for g in range(groups):
        xg = xp[:, g * Cing:(g + 1) * Cing]              # (N, Cing, H, Wp)
        cols = np.empty((N, Cing, kh, kw, Hout, Wout), dtype=x.dtype)
        for i in range(kh):
            for j in range(kw):
                cols[:, :, i, j] = xg[:, :, i:i + Hout, j:j + Wout]
        cols = cols.reshape(N, Cing * kh * kw, Hout * Wout)
        Wg = W[g * Coutg:(g + 1) * Coutg].reshape(Coutg, Cing * kh * kw)
        yg = np.einsum("oc,ncp->nop", Wg, cols, optimize=True)
        y[:, g * Coutg:(g + 1) * Coutg] = yg.reshape(N, Coutg, Hout, Wout)
        cols_per_group.append(cols)
    cache = (x.shape, xp.shape, W, groups, kh, kw, pad_l, Hout, Wout, cols_per_group)
    return y, cache


def conv2d_backward(dy: np.ndarray, cache):
    """Backward pass for :func:`conv2d_forward`. Returns ``(dx, dW)``."""
    x_shape, xp_shape, W, groups, kh, kw, pad_l, Hout, Wout, cols_per_group = cache
    N, Cin, H, Wd = x_shape
    Cout, Cing, _, _ = W.shape
    Coutg = Cout // groups
    dW = np.zeros(W.shape, dtype=dy.dtype)
    dxp = np.zeros(xp_shape, dtype=dy.dtype)
    for g in range(groups):
        cols = cols_per_group[g]                          # (N, Cing*kh*kw, P)
        dyg = dy[:, g * Coutg:(g + 1) * Coutg].reshape(N, Coutg, Hout * Wout)
        dWg = np.einsum("nop,ncp->oc", dyg, cols, optimize=True)
        dW[g * Coutg:(g + 1) * Coutg] = dWg.reshape(Coutg, Cing, kh, kw)
        Wg = W[g * Coutg:(g + 1) * Coutg].reshape(Coutg, Cing * kh * kw)
        dcols = np.einsum("oc,nop->ncp", Wg, dyg, optimize=True)
        dcols = dcols.reshape(N, Cing, kh, kw, Hout, Wout)
        for i in range(kh):
            for j in range(kw):
                dxp[:, g * Cing:(g + 1) * Cing, i:i + Hout, j:j + Wout] += dcols[:, :, i, j]
    # Remove time padding.
    if pad_l > 0 or xp_shape[3] != Wd:
        dx = dxp[:, :, :, pad_l:pad_l + Wd]
    else:
        dx = dxp
    return dx, dW


# --------------------------------------------------------------------------- #
# BatchNorm over (N, H, W) per channel.
# --------------------------------------------------------------------------- #
def bn_forward(x, gamma, beta, running, momentum, eps, train):
    """BatchNorm2d. ``running`` is a mutable dict with 'mean'/'var' (updated in train)."""
    if train:
        mean = x.mean(axis=(0, 2, 3))
        var = x.var(axis=(0, 2, 3))
        running["mean"] = (1 - momentum) * running["mean"] + momentum * mean
        running["var"] = (1 - momentum) * running["var"] + momentum * var
    else:
        mean = running["mean"]
        var = running["var"]
    g = gamma[None, :, None, None]
    b = beta[None, :, None, None]
    xhat = (x - mean[None, :, None, None]) / np.sqrt(var[None, :, None, None] + eps)
    y = g * xhat + b
    cache = (xhat, var, eps, gamma, x.shape, train, x, mean)
    return y, cache


def bn_backward(dy, cache):
    """Backward for :func:`bn_forward`. Returns ``(dx, dgamma, dbeta)``."""
    xhat, var, eps, gamma, shape, train, x, mean = cache
    N, C, H, W = shape
    m = N * H * W
    dgamma = (dy * xhat).sum(axis=(0, 2, 3))
    dbeta = dy.sum(axis=(0, 2, 3))
    if not train:
        std = np.sqrt(var + eps)[None, :, None, None]
        dx = dy * gamma[None, :, None, None] / std
        return dx, dgamma, dbeta
    istd = 1.0 / np.sqrt(var + eps)
    g = gamma[None, :, None, None]
    istd_b = istd[None, :, None, None]
    dxhat = dy * g
    sum_dxhat = dxhat.sum(axis=(0, 2, 3))[None, :, None, None]
    sum_dxhat_xhat = (dxhat * xhat).sum(axis=(0, 2, 3))[None, :, None, None]
    dx = istd_b / m * (m * dxhat - sum_dxhat - xhat * sum_dxhat_xhat)
    return dx, dgamma, dbeta


# --------------------------------------------------------------------------- #
# Elementwise + pooling ops.
# --------------------------------------------------------------------------- #
def elu_forward(x, alpha=1.0):
    y = np.where(x > 0, x, alpha * (np.expm1(x)))
    return y, (x, alpha, y)


def elu_backward(dy, cache):
    x, alpha, y = cache
    grad = np.where(x > 0, 1.0, y + alpha)
    return dy * grad


def avgpool_time_forward(x, k):
    """Average-pool the last (time) axis by an integer factor ``k`` (drops remainder)."""
    N, C, H, W = x.shape
    Wk = (W // k) * k
    xt = x[:, :, :, :Wk].reshape(N, C, H, Wk // k, k)
    y = xt.mean(axis=4)
    return y, (x.shape, k, Wk)


def avgpool_time_backward(dy, cache):
    shape, k, Wk = cache
    N, C, H, W = shape
    dx = np.zeros(shape, dtype=dy.dtype)
    up = np.repeat(dy, k, axis=3) / k
    dx[:, :, :, :Wk] = up
    return dx


def dropout_forward(x, p, train, rng):
    if not train or p <= 0:
        return x, None
    mask = (rng.random(x.shape) >= p) / (1.0 - p)
    return x * mask, mask


def dropout_backward(dy, mask):
    return dy if mask is None else dy * mask


# --------------------------------------------------------------------------- #
# The model.
# --------------------------------------------------------------------------- #
@dataclass
class EEGNetConfig:
    C: int = 8           # channels (locked montage)
    T: int = 600         # samples in maintenance window (3 s @ 200 Hz)
    F1: int = 8          # temporal filters
    D: int = 2           # spatial depth multiplier
    F2: int = 16         # separable (pointwise) filters
    kt: int = 64         # temporal kernel (~0.32 s @ 200 Hz, ~half EEGNet's fs/2 rule)
    kt2: int = 16        # separable temporal kernel
    p1: int = 4          # first avg-pool factor
    p2: int = 8          # second avg-pool factor
    dropout: float = 0.5
    bn_momentum: float = 0.1
    bn_eps: float = 1e-5


class EEGNet:
    """Compact EEGNet with hand-written forward/backward and an Adam optimizer."""

    def __init__(self, cfg: EEGNetConfig, seed: int = 0):
        self.cfg = cfg
        rng = np.random.default_rng(seed)
        c = cfg
        # He-style init for conv weights; small for the dense head.
        self.params = {
            "Wt": rng.standard_normal((c.F1, 1, 1, c.kt)) * np.sqrt(2.0 / (c.kt)),
            "g1": np.ones(c.F1), "b1": np.zeros(c.F1),
            "Wd": rng.standard_normal((c.F1 * c.D, 1, c.C, 1)) * np.sqrt(2.0 / (c.C)),
            "g2": np.ones(c.F1 * c.D), "b2": np.zeros(c.F1 * c.D),
            "Ws": rng.standard_normal((c.F1 * c.D, 1, 1, c.kt2)) * np.sqrt(2.0 / (c.kt2)),
            "Wp": rng.standard_normal((c.F2, c.F1 * c.D, 1, 1)) * np.sqrt(2.0 / (c.F1 * c.D)),
            "g3": np.ones(c.F2), "b3": np.zeros(c.F2),
            "Wfc": None, "bfc": np.zeros(2),  # Wfc lazily sized after first forward
        }
        self.running = {
            "bn1": {"mean": np.zeros(c.F1), "var": np.ones(c.F1)},
            "bn2": {"mean": np.zeros(c.F1 * c.D), "var": np.ones(c.F1 * c.D)},
            "bn3": {"mean": np.zeros(c.F2), "var": np.ones(c.F2)},
        }
        self._fc_rng = rng
        self.adam = None

    # -- forward ----------------------------------------------------------- #
    def forward(self, x, train, rng=None):
        """Run the network. ``x`` is (N, 1, C, T). Returns (logits, cache)."""
        c, p = self.cfg, self.params
        cache = {}

        z, cache["c1"] = conv2d_forward(x, p["Wt"], groups=1, same_time=True)
        z, cache["bn1"] = bn_forward(z, p["g1"], p["b1"], self.running["bn1"],
                                     c.bn_momentum, c.bn_eps, train)

        z, cache["c2"] = conv2d_forward(z, p["Wd"], groups=c.F1, same_time=False)
        z, cache["bn2"] = bn_forward(z, p["g2"], p["b2"], self.running["bn2"],
                                     c.bn_momentum, c.bn_eps, train)
        z, cache["el2"] = elu_forward(z)
        z, cache["ap1"] = avgpool_time_forward(z, c.p1)
        z, cache["dp1"] = dropout_forward(z, c.dropout, train, rng)

        z, cache["c3"] = conv2d_forward(z, p["Ws"], groups=c.F1 * c.D, same_time=True)
        z, cache["c4"] = conv2d_forward(z, p["Wp"], groups=1, same_time=False)
        z, cache["bn3"] = bn_forward(z, p["g3"], p["b3"], self.running["bn3"],
                                     c.bn_momentum, c.bn_eps, train)
        z, cache["el3"] = elu_forward(z)
        z, cache["ap2"] = avgpool_time_forward(z, c.p2)
        z, cache["dp2"] = dropout_forward(z, c.dropout, train, rng)

        N = z.shape[0]
        flat = z.reshape(N, -1)
        cache["flat_shape"] = z.shape
        if p["Wfc"] is None:
            n_flat = flat.shape[1]
            p["Wfc"] = self._fc_rng.standard_normal((n_flat, 2)) * np.sqrt(1.0 / n_flat)
        logits = flat @ p["Wfc"] + p["bfc"]
        cache["flat"] = flat
        return logits, cache

    # -- loss + backward --------------------------------------------------- #
    @staticmethod
    def softmax_ce(logits, y, class_weight):
        """Class-weighted softmax cross-entropy. Returns (loss, dlogits, probs)."""
        z = logits - logits.max(axis=1, keepdims=True)
        ez = np.exp(z)
        probs = ez / ez.sum(axis=1, keepdims=True)
        w = class_weight[y]
        ll = -np.log(probs[np.arange(len(y)), y] + 1e-12)
        loss = float((w * ll).sum() / w.sum())
        onehot = np.zeros_like(probs)
        onehot[np.arange(len(y)), y] = 1.0
        dlogits = (probs - onehot) * w[:, None] / w.sum()
        return loss, dlogits, probs

    def backward(self, dlogits, cache):
        """Backprop ``dlogits`` through the cached forward pass. Returns a grad dict."""
        p = self.params
        grads = {}
        flat = cache["flat"]
        grads["Wfc"] = flat.T @ dlogits
        grads["bfc"] = dlogits.sum(axis=0)
        dflat = dlogits @ p["Wfc"].T
        dz = dflat.reshape(cache["flat_shape"])

        dz = dropout_backward(dz, cache["dp2"])
        dz = avgpool_time_backward(dz, cache["ap2"])
        dz = elu_backward(dz, cache["el3"])
        dz, grads["g3"], grads["b3"] = bn_backward(dz, cache["bn3"])
        dz, grads["Wp"] = conv2d_backward(dz, cache["c4"])
        dz, grads["Ws"] = conv2d_backward(dz, cache["c3"])

        dz = dropout_backward(dz, cache["dp1"])
        dz = avgpool_time_backward(dz, cache["ap1"])
        dz = elu_backward(dz, cache["el2"])
        dz, grads["g2"], grads["b2"] = bn_backward(dz, cache["bn2"])
        dz, grads["Wd"] = conv2d_backward(dz, cache["c2"])

        dz, grads["g1"], grads["b1"] = bn_backward(dz, cache["bn1"])
        _, grads["Wt"] = conv2d_backward(dz, cache["c1"])
        return grads

    # -- Adam -------------------------------------------------------------- #
    def _init_adam(self):
        self.adam = {
            "m": {k: np.zeros_like(v) for k, v in self.params.items() if v is not None},
            "v": {k: np.zeros_like(v) for k, v in self.params.items() if v is not None},
            "t": 0,
        }

    def adam_step(self, grads, lr=1e-3, beta1=0.9, beta2=0.999, eps=1e-8, weight_decay=0.0):
        """One Adam update over all parameters (with optional decoupled weight decay)."""
        if self.adam is None or set(self.adam["m"]) != {k for k, v in self.params.items() if v is not None}:
            self._init_adam()
        a = self.adam
        a["t"] += 1
        for k, g in grads.items():
            if weight_decay and k.startswith("W"):
                self.params[k] -= lr * weight_decay * self.params[k]
            a["m"][k] = beta1 * a["m"][k] + (1 - beta1) * g
            a["v"][k] = beta2 * a["v"][k] + (1 - beta2) * (g * g)
            mhat = a["m"][k] / (1 - beta1 ** a["t"])
            vhat = a["v"][k] / (1 - beta2 ** a["t"])
            self.params[k] -= lr * mhat / (np.sqrt(vhat) + eps)


# --------------------------------------------------------------------------- #
# Gradient check (the implementation's stop-or-go validation).
# --------------------------------------------------------------------------- #
def _max_rel_error(analytic, P, loss_fn, eps):
    """Central-difference ``loss_fn`` w.r.t. every entry of ``P`` vs ``analytic``."""
    num = np.zeros_like(P)
    it = np.nditer(P, flags=["multi_index"])
    while not it.finished:
        idx = it.multi_index
        orig = P[idx]
        P[idx] = orig + eps
        lp = loss_fn()
        P[idx] = orig - eps
        lm = loss_fn()
        P[idx] = orig
        num[idx] = (lp - lm) / (2 * eps)
        it.iternext()
    denom = np.maximum(np.abs(analytic) + np.abs(num), 1e-8)
    return float((np.abs(analytic - num) / denom).max())


def _check_bn_train(seed, eps, tol):
    """Isolated finite-difference check of train-mode BatchNorm (x, gamma, beta grads).

    Stacked train-mode BatchNorms make a whole-network finite-difference of an early
    layer's affine params ill-conditioned (a downstream BN re-normalizes the perturbation
    away), so the train-mode BN backward is verified here in isolation, where it is
    well-conditioned.
    """
    rng = np.random.default_rng(seed)
    N, C, H, W = 6, 4, 3, 10
    x = rng.standard_normal((N, C, H, W))
    gamma = rng.standard_normal(C)
    beta = rng.standard_normal(C)
    g_out = rng.standard_normal((N, C, H, W))
    run = {"mean": np.zeros(C), "var": np.ones(C)}

    def loss():
        y, _ = bn_forward(x, gamma, beta, dict(run), 0.1, 1e-5, train=True)
        return float((y * g_out).sum())

    y, cache = bn_forward(x, gamma, beta, dict(run), 0.1, 1e-5, train=True)
    dx, dgamma, dbeta = bn_backward(g_out, cache)
    errs = {
        "bn_train.x": _max_rel_error(dx, x, loss, eps),
        "bn_train.gamma": _max_rel_error(dgamma, gamma, loss, eps),
        "bn_train.beta": _max_rel_error(dbeta, beta, loss, eps),
    }
    worst = max(errs.values())
    assert worst < tol, f"train-mode BN gradient check FAILED: {errs}"
    return errs


def gradient_check(seed: int = 0, eps: float = 1e-6, tol: float = 1e-4) -> dict:
    """Validate the full backprop against finite differences.

    Two complementary checks (dropout off throughout):
      1. Train-mode BatchNorm in isolation (:func:`_check_bn_train`), where the batch-stat
         coupling is present but well-conditioned.
      2. The full network in eval mode (BatchNorm uses fixed running stats populated by a
         prior train pass, so each BN is a fixed affine map). This is well-conditioned for
         every parameter -- including the first BN's affine params -- and exercises all
         convolutions, the dense head, ELU, pooling, and eval-mode BN backward.

    Returns a dict of per-parameter max relative error; raises AssertionError on failure.
    """
    errors = _check_bn_train(seed, eps, tol)

    rng = np.random.default_rng(seed)
    cfg = EEGNetConfig(C=4, T=48, F1=3, D=2, F2=4, kt=8, kt2=4, p1=2, p2=2, dropout=0.0)
    net = EEGNet(cfg, seed=seed)
    N = 6
    x = rng.standard_normal((N, 1, cfg.C, cfg.T))
    y = rng.integers(0, 2, size=N)
    cw = np.array([1.0, 1.0])

    # Populate running stats with one train pass, then freeze (eval mode) for the check.
    net.forward(x, train=True, rng=None)

    def loss_of_params():
        logits, _ = net.forward(x, train=False, rng=None)
        loss, _, _ = net.softmax_ce(logits, y, cw)
        return loss

    logits, cache = net.forward(x, train=False, rng=None)
    _, dlogits, _ = net.softmax_ce(logits, y, cw)
    grads = net.backward(dlogits, cache)

    for name in grads:
        errors[name] = _max_rel_error(grads[name], net.params[name], loss_of_params, eps)
    worst = max(errors.values())
    assert worst < tol, f"gradient check FAILED: max rel error {worst:.2e} > {tol:.0e}\n{errors}"
    return errors
