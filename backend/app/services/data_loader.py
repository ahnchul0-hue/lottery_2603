import json
from pathlib import Path

from app.schemas.lottery import LotteryDraw


class DataLoader:
    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)
        self.all_draws: list[LotteryDraw] = []
        self._by_machine: dict[str, list[LotteryDraw]] = {}
        self.metadata: dict = {}

    def load_and_validate(self) -> None:
        """Load JSON, validate every record, pre-filter by machine."""
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self.metadata = raw["metadata"]
        errors: list[str] = []

        for i, record in enumerate(raw["lottery_data"]):
            try:
                draw = LotteryDraw(
                    round_number=record["회차"],
                    machine=record["호기"],
                    numbers=record["1등_당첨번호"],
                    odd_even_ratio=record["홀짝_비율"],
                    high_low_ratio=record["고저_비율"],
                    ac_value=record["AC값"],
                    tail_sum=record["끝수합"],
                    total_sum=record["총합"],
                )
                self.all_draws.append(draw)
            except Exception as e:
                errors.append(f"Record {i} (round {record.get('회차', '?')}): {e}")

        if errors:
            raise ValueError(
                f"Data validation failed for {len(errors)} records:\n"
                + "\n".join(errors)
            )

        # Pre-filter by machine
        for machine in ["1호기", "2호기", "3호기"]:
            self._by_machine[machine] = sorted(
                [d for d in self.all_draws if d.machine == machine],
                key=lambda d: d.round_number,
            )

    def get_draws_for_machine(self, machine: str) -> list[LotteryDraw]:
        if machine not in self._by_machine:
            raise ValueError(
                f"Unknown machine: {machine}. Valid: 1호기, 2호기, 3호기"
            )
        return self._by_machine[machine]

    @property
    def total_records(self) -> int:
        return len(self.all_draws)
