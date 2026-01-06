"""Base agent interface for all agents in the system.

This module defines the abstract base class that all agents (Scout, Strategist, Executor)
must implement to ensure consistent behavior and API across the agent system.
"""

from abc import ABC, abstractmethod

from src.domain.models import GameState


class BaseAgent(ABC):
    """Abstract base class for all agents.

    All agents in the system inherit from this class and implement the analyze() method
    to provide their specific functionality (threat detection, strategy, execution).
    """

    @abstractmethod
    def analyze(self, game_state: GameState) -> object:
        """Analyze the game state and return agent-specific results.

        Args:
            game_state: Current game state to analyze

        Returns:
            Agent-specific result object (BoardAnalysis, Strategy, MoveExecution)

        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        pass
