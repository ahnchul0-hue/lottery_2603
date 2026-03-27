"""Strategy registry for prediction strategies.

Provides STRATEGY_MAP for looking up strategies by name,
and get_strategy() for safe access with error handling.
"""

from app.strategies.balance import BalanceStrategy
from app.strategies.base import PredictionStrategy
from app.strategies.composite import CompositeStrategy
from app.strategies.frequency import FrequencyStrategy
from app.strategies.pattern import PatternStrategy
from app.strategies.range import RangeStrategy

STRATEGY_MAP: dict[str, PredictionStrategy] = {
    "frequency": FrequencyStrategy(),
    "pattern": PatternStrategy(),
    "range": RangeStrategy(),
    "balance": BalanceStrategy(),
    "composite": CompositeStrategy(),
}


def get_strategy(name: str) -> PredictionStrategy:
    """Get a prediction strategy by name.

    Args:
        name: Strategy identifier (e.g., 'frequency').

    Returns:
        PredictionStrategy instance.

    Raises:
        KeyError: If strategy name is not registered.
    """
    if name not in STRATEGY_MAP:
        raise KeyError(
            f"Unknown strategy: {name}. Available: {list(STRATEGY_MAP.keys())}"
        )
    return STRATEGY_MAP[name]
