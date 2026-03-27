"""Base prediction strategy abstract class.

Defines the PredictionStrategy ABC that all strategies must implement.
Extensible via subclassing -- new strategies can be added without
modifying existing code (Open/Closed Principle).
"""

from abc import ABC, abstractmethod

from app.schemas.lottery import LotteryDraw


class PredictionStrategy(ABC):
    """Abstract base class for lottery number prediction strategies.

    Subclasses must implement:
    - name: Machine-readable strategy identifier
    - display_name: Human-readable strategy name (Korean)
    - generate: Core prediction logic
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Machine-readable strategy identifier (e.g., 'frequency')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable strategy name (e.g., '빈도 전략')."""
        ...

    @abstractmethod
    def generate(
        self,
        draws: list[LotteryDraw],
        weighted_frequencies: dict[int, float],
    ) -> list[list[int]]:
        """Generate prediction game sets.

        Args:
            draws: Machine-filtered LotteryDraw list sorted by round_number ascending.
            weighted_frequencies: Dict mapping number (1-45) -> weighted frequency.

        Returns:
            List of games, each game is a list of 6 unique sorted integers in [1, 45].
        """
        ...
