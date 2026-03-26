from app.config import settings
from app.schemas.lottery import LotteryDraw


class DecayEngine:
    """Compute time-decay-weighted number frequencies from lottery draws.

    Uses exponential decay: weight = 0.5^(draws_since / halflife)
    where draws_since=0 for the newest draw.

    Per D-01: Exponential decay formula
    Per D-02: halflife defaults to 30
    Per D-04: Applies to number frequency (1-45) only
    """

    def __init__(self, halflife: int | None = None):
        self.halflife = halflife if halflife is not None else settings.DECAY_HALFLIFE

    def compute_weights(self, draws: list[LotteryDraw]) -> list[float]:
        """Compute per-draw decay weights.

        Args:
            draws: LotteryDraw list sorted ascending by round_number (oldest first).
                   This is the order DataLoader.get_draws_for_machine() returns.

        Returns:
            Weights in same order as input. Newest draw (last) = 1.0,
            oldest draw (first) = smallest weight. Raw values, not normalized.
        """
        n = len(draws)
        if n == 0:
            return []
        # draws_since for index i: n - 1 - i
        # Newest (i=n-1): draws_since=0, weight=1.0
        # Oldest (i=0): draws_since=n-1, weight=0.5^((n-1)/halflife)
        return [0.5 ** ((n - 1 - i) / self.halflife) for i in range(n)]

    def compute_weighted_frequencies(
        self, draws: list[LotteryDraw]
    ) -> dict[int, float]:
        """Compute weighted frequency for each number 1-45.

        Per D-08: Input is machine-filtered LotteryDraw list,
        output is dict[int, float] mapping number -> weighted frequency.

        Args:
            draws: Machine-filtered LotteryDraw list sorted by round_number ascending.

        Returns:
            Dict mapping number (1-45) -> weighted frequency (float).
            Numbers that never appeared have value 0.0.
        """
        weights = self.compute_weights(draws)
        freq: dict[int, float] = {n: 0.0 for n in range(1, 46)}

        for draw, weight in zip(draws, weights):
            for number in draw.numbers:
                freq[number] += weight

        return freq
