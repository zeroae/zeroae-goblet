"""
The Chalice Blueprint and Configuration for the Goblin framework.
"""
from .blueprint import bp
from ..config import configure

__all__ = ["bp", "configure"]
