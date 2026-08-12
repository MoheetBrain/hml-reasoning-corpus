"""Minimal semantic mutations supported by the frozen verifier."""

from .semantic_firewall import Mutation, mutate_valid_case

__all__ = ["Mutation", "mutate_valid_case"]
