"""Shared utilities for the Dandelion EEG -> deep/MTL activity project.

Modules:
    nix_io    -- read the simultaneous scalp/iEEG/unit NIX (.h5) session files.
    epoching  -- cut analysis windows (e.g. the maintenance period) from epochs.

All scripts import shared logic from here rather than copy-pasting it, per the
Dandelion software-engineering standards.
"""
