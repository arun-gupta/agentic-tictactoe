"""Agent system for AI decision making.

This package contains the agent implementations (Scout, Strategist, Executor)
that work together to analyze the game state and make optimal moves.
"""

from src.agents.base import BaseAgent
from src.agents.scout import ScoutAgent

__all__ = ["BaseAgent", "ScoutAgent"]
