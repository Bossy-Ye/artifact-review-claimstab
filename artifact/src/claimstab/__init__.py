"""Minimal reviewer-facing extract of the CLAIMSTAB-QC verdict-computation core.

This is NOT the full framework: it bundles only the dependency-light modules that
support Section IV's verdict logic (Wilson S/U/R, relation checkers, comparison
objects). It intentionally does not import the qiskit-dependent pipeline/runner/
experiment code. See artifact/src/README.md.
"""
__version__ = "0.1.0-artifact-min"
