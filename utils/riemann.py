"""Affine-invariant Riemannian geometry on SPD covariance matrices.

The covariance/Riemannian rungs of the model ladder treat each trial's per-band
channel covariance as a point on the manifold of symmetric positive-definite (SPD)
matrices, rather than as a flat vector. Two operations come out of that view:

  * **Tangent-space projection at the geometric mean.** Each covariance is whitened by
    the training-set Riemannian mean and mapped through the matrix logarithm into a
    Euclidean tangent space. Unlike the matrix-log-at-identity vectorization used by the
    rung-1 features, this references the data's own center of mass, which is the standard
    Riemannian classification pipeline (Barachant et al., 2012).
  * **Minimum-distance-to-mean (MDM).** Each class is summarized by the Riemannian mean
    of its training covariances; a test covariance is labeled by the nearest class mean
    under the affine-invariant distance. This is a fully geometric classifier with no
    Euclidean model on top.

Everything here is pure NumPy/SciPy and operates on the 8x8 (or 6x6 brain-only) shrunk
SPD covariances already shipped in the feature bundle, so the project takes on no new
dependency for the Riemannian rungs. All matrices passed in are assumed SPD (the bundle
shrinks them toward a scaled identity before storage); functions still clip eigenvalues
to a small floor so a numerically borderline matrix cannot produce a NaN.

References:
  Barachant, Bonnet, Congedo, Jutten (2012), "Multiclass Brain-Computer Interface
  Classification by Riemannian Geometry", IEEE TBME 59(4):920-928.
  doi:10.1109/TBME.2011.2172210
"""

from __future__ import annotations

import numpy as np

_EIG_FLOOR = 1e-12  # eigenvalue floor so log/inverse stay finite on borderline SPD inputs


def _sym(mats: np.ndarray) -> np.ndarray:
    """Symmetrize a stack of square matrices (kills tiny asymmetries from round-off)."""
    return 0.5 * (mats + np.transpose(mats, (0, 2, 1)))


def _eig_apply(mats: np.ndarray, fun) -> np.ndarray:
    """Apply a scalar function to the eigenvalues of a stack of symmetric matrices.

    No eigenvalue clipping happens here -- each caller decides whether its function needs
    a positivity floor. This matters for the matrix exponential, whose argument is a
    tangent vector with genuinely negative eigenvalues that must not be clipped.

    Args:
        mats: (n, k, k) stack of symmetric matrices.
        fun: callable mapping a (n, k) array of eigenvalues to transformed eigenvalues.

    Returns:
        (n, k, k) stack of symmetric matrices V @ diag(fun(w)) @ V^T.
    """
    w, V = np.linalg.eigh(_sym(np.asarray(mats, dtype=np.float64)))
    fw = fun(w)
    return (V * fw[:, None, :]) @ np.transpose(V, (0, 2, 1))


def _floor(w: np.ndarray) -> np.ndarray:
    """Clip eigenvalues to a positive floor (for sqrt/inverse/log, which need w > 0)."""
    return np.clip(w, _EIG_FLOOR, None)


def spd_sqrt(mats: np.ndarray) -> np.ndarray:
    """Matrix square root of a stack of SPD matrices."""
    return _eig_apply(mats, lambda w: np.sqrt(_floor(w)))


def spd_invsqrt(mats: np.ndarray) -> np.ndarray:
    """Inverse matrix square root of a stack of SPD matrices."""
    return _eig_apply(mats, lambda w: 1.0 / np.sqrt(_floor(w)))


def spd_logm(mats: np.ndarray) -> np.ndarray:
    """Matrix logarithm of a stack of SPD matrices."""
    return _eig_apply(mats, lambda w: np.log(_floor(w)))


def spd_expm(mats: np.ndarray) -> np.ndarray:
    """Matrix exponential of a stack of symmetric matrices (no eigenvalue floor)."""
    return _eig_apply(mats, np.exp)


def regularize_spd(covs: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    """Restore strict positive-definiteness to (possibly float32-degraded) covariances.

    The feature bundle stores shrunk covariances as float32; the wide dynamic range of
    per-band EEG power can cost a matrix its smallest eigenvalue in that cast, leaving it
    numerically singular (condition number -> inf). Affine-invariant geometry requires
    strict SPD inputs, so each matrix gets a trace-proportional ridge added to its
    diagonal. The ridge is tiny relative to the matrix scale, so it restores invertibility
    without materially changing the geometry.

    Args:
        covs: (..., k, k) stack of (nearly) SPD matrices.
        ridge: ridge as a fraction of each matrix's mean eigenvalue (trace / k).

    Returns:
        float64 array, same shape, with a small multiple of the identity added.
    """
    covs = np.asarray(covs, dtype=np.float64)
    k = covs.shape[-1]
    trace = np.trace(covs, axis1=-2, axis2=-1)            # (...,)
    bump = (ridge * trace / k)[..., None, None] * np.eye(k)
    return covs + bump


def riemannian_mean(
    covs: np.ndarray, tol: float = 1e-8, max_iter: int = 100
) -> np.ndarray:
    """Affine-invariant Riemannian (Frechet) mean of a stack of SPD matrices.

    Iterates the Karcher-flow fixed-point scheme: project every matrix into the tangent
    space at the current mean, step along the average tangent vector, and map back to
    the manifold. A full unit step oscillates on real EEG covariances, which span a wide
    dynamic range, so the step size ``nu`` is damped adaptively -- shrunk gently while the
    iteration is making progress and halved whenever a step fails to reduce the gradient
    norm. This is the standard robust scheme (as in pyriemann's ``mean_riemann``) and
    converges on the manifold's non-positive curvature. Convergence is declared when the
    Frobenius norm of the average tangent vector drops below ``tol``.

    Args:
        covs: (n, k, k) stack of SPD matrices.
        tol: convergence threshold on the mean tangent-vector norm.
        max_iter: maximum number of iterations.

    Returns:
        (k, k) SPD Riemannian mean.

    Raises:
        ValueError if ``covs`` is not a non-empty 3-D stack of square matrices.
    """
    covs = np.asarray(covs, dtype=np.float64)
    if covs.ndim != 3 or covs.shape[1] != covs.shape[2] or covs.shape[0] == 0:
        raise ValueError(f"covs must be a non-empty (n, k, k) stack; got {covs.shape}.")
    mean = _sym(covs.mean(axis=0)[None])[0]  # arithmetic-mean warm start
    nu = 1.0
    tau = np.inf
    crit = np.inf
    for _ in range(max_iter):
        m_invsqrt = spd_invsqrt(mean[None])[0]
        whitened = m_invsqrt @ covs @ m_invsqrt           # (n, k, k)
        avg_tan = spd_logm(whitened).mean(axis=0)         # (k, k) average tangent vector
        crit = float(np.linalg.norm(avg_tan, ord="fro"))
        if crit < tol or nu < tol:
            break
        m_sqrt = spd_sqrt(mean[None])[0]
        mean = m_sqrt @ spd_expm((nu * avg_tan)[None])[0] @ m_sqrt
        mean = _sym(mean[None])[0]
        # Adaptive damping: shrink the step gently while progressing, halve it on a stall.
        h = nu * crit
        if h < tau:
            nu = 0.95 * nu
            tau = h
        else:
            nu = 0.5 * nu
    return mean


def tangent_space(covs: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """Project SPD matrices into the tangent space at a reference SPD matrix.

    Whitens each covariance by ``ref`` and vectorizes the upper triangle of the matrix
    logarithm with the off-diagonal isometry weight (sqrt(2)), so that Euclidean distance
    in the returned vectors approximates Riemannian distance near ``ref``.

    Args:
        covs: (n, k, k) stack of SPD matrices.
        ref: (k, k) SPD reference (typically the training-set Riemannian mean).

    Returns:
        (n, k*(k+1)/2) tangent-space feature matrix.
    """
    covs = np.asarray(covs, dtype=np.float64)
    ref_invsqrt = spd_invsqrt(np.asarray(ref, dtype=np.float64)[None])[0]
    whitened = ref_invsqrt @ covs @ ref_invsqrt
    logs = spd_logm(whitened)                              # (n, k, k) symmetric
    k = covs.shape[1]
    iu, ju = np.triu_indices(k)
    weights = np.where(iu == ju, 1.0, np.sqrt(2.0))        # isometry weight per entry
    return logs[:, iu, ju] * weights


def airm_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Affine-invariant Riemannian distance between two SPD matrices.

    d(A, B) = || log(A^{-1/2} B A^{-1/2}) ||_F = sqrt(sum_i log(lambda_i)^2), where
    lambda_i are the generalized eigenvalues of (A, B).

    Args:
        a, b: (k, k) SPD matrices.

    Returns:
        Non-negative scalar distance.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a_invsqrt = spd_invsqrt(a[None])[0]
    w = np.linalg.eigvalsh(_sym((a_invsqrt @ b @ a_invsqrt)[None])[0])
    w = np.clip(w, _EIG_FLOOR, None)
    return float(np.sqrt(np.sum(np.log(w) ** 2)))
