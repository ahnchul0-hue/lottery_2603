from app.schemas.lottery import LotteryDraw


def compute_heatmap_data(
    by_machine: dict[str, list[LotteryDraw]],
) -> list[dict]:
    """Compute per-machine per-number frequency deviation from expected.

    Deviation = (actual_count - expected_count) / expected_count.
    Expected count per number = total_draws * (6 / 45).
    """
    machines = ["1호기", "2호기", "3호기"]
    result = []
    for machine in machines:
        draws = by_machine.get(machine, [])
        total = len(draws)
        expected_per_number = total * (6 / 45)

        freq: dict[int, int] = {n: 0 for n in range(1, 46)}
        for draw in draws:
            for num in draw.numbers:
                freq[num] += 1

        deviations: dict[str, float] = {}
        for num in range(1, 46):
            if expected_per_number > 0:
                deviations[str(num)] = round(
                    (freq[num] - expected_per_number) / expected_per_number, 4
                )
            else:
                deviations[str(num)] = 0.0

        result.append(
            {
                "machine": machine,
                "deviations": deviations,
                "total_draws": total,
            }
        )
    return result
