"""Shared helpers for MTL mechanism analyses.

The mechanism layer asks whether scalp-derived working-memory-load signatures are tied
to directly recorded medial-temporal-lobe activity. These helpers keep the anatomical
definition of "MTL" consistent across the coverage audit and later mechanism probes.
"""

from __future__ import annotations


# Anatomy region-code prefixes (the token before the first comma) that are MTL core.
MTL_REGIONS = {
    "Hipp": "hippocampus",
    "Amyg": "amygdala",
    "PhG": "parahippocampal",
}

# The canonical deep targets a coupling readout needs at least one of.
DEEP_MTL = {"hippocampus", "amygdala"}


def region_of(anatomy: str) -> tuple[str, str]:
    """Map a raw anatomy string to (mtl_subregion_or_empty, coarse_class).

    Returns:
        (subregion, klass) where subregion is one of ``MTL_REGIONS.values()`` or an
        empty string, and klass is ``mtl``, ``non_mtl``, or ``unlabeled``.
    """
    if anatomy == "no_label_found" or not anatomy:
        return "", "unlabeled"
    prefix = anatomy.split(",")[0].strip()
    if prefix in MTL_REGIONS:
        return MTL_REGIONS[prefix], "mtl"
    return "", "non_mtl"


def hemisphere_of(anatomy: str) -> str:
    """Best-effort hemisphere from the anatomy string."""
    text = anatomy.lower()
    if "left" in text:
        return "left"
    if "right" in text:
        return "right"
    return "unknown"


def mtl_contact_rows(electrode_records: list[dict]) -> list[dict]:
    """Return MTL contacts annotated with subregion and hemisphere.

    Args:
        electrode_records: records from ``nix_io.read_ieeg_electrode_info``.

    Returns:
        One row per contact whose anatomy maps to the MTL definition.
    """
    rows = []
    for rec in electrode_records:
        subregion, klass = region_of(rec["anatomy"])
        if klass != "mtl":
            continue
        rows.append({
            "channel": rec["channel"],
            "mtl_subregion": subregion,
            "hemisphere": hemisphere_of(rec["anatomy"]),
            "anatomy": rec["anatomy"],
            "mni_xyz": rec.get("mni_xyz"),
        })
    return rows
