import pytest
from pydantic import ValidationError

from app.config import settings
from app.schemas.lottery import LotteryDraw
from app.services.data_loader import DataLoader


@pytest.fixture(scope="module")
def loader():
    dl = DataLoader(settings.DATA_PATH)
    dl.load_and_validate()
    return dl


def test_load_all_records(loader):
    """DataLoader loads all 417 records from new_res.json."""
    assert loader.total_records == 417


def test_filter_by_machine_1hoogi(loader):
    """1호기 has 134 draws."""
    draws = loader.get_draws_for_machine("1호기")
    assert len(draws) == 134


def test_filter_by_machine_2hoogi(loader):
    """2호기 has 136 draws."""
    draws = loader.get_draws_for_machine("2호기")
    assert len(draws) == 136


def test_filter_by_machine_3hoogi(loader):
    """3호기 has 147 draws."""
    draws = loader.get_draws_for_machine("3호기")
    assert len(draws) == 147


def test_invalid_machine_raises(loader):
    """Unknown machine raises ValueError."""
    with pytest.raises(ValueError, match="Unknown machine"):
        loader.get_draws_for_machine("4호기")


def test_all_numbers_in_range(loader):
    """Every draw's numbers are between 1 and 45."""
    for draw in loader.all_draws:
        for n in draw.numbers:
            assert 1 <= n <= 45, f"Round {draw.round_number}: {n} out of range"


def test_all_numbers_sorted(loader):
    """Every draw's numbers are in ascending order."""
    for draw in loader.all_draws:
        assert draw.numbers == sorted(draw.numbers), (
            f"Round {draw.round_number}: not sorted {draw.numbers}"
        )


def test_all_numbers_count_six(loader):
    """Every draw has exactly 6 numbers."""
    for draw in loader.all_draws:
        assert len(draw.numbers) == 6, (
            f"Round {draw.round_number}: {len(draw.numbers)} numbers"
        )


def test_validation_rejects_wrong_count():
    """LotteryDraw rejects records with != 6 numbers."""
    with pytest.raises(ValidationError, match="Expected 6 numbers"):
        LotteryDraw(
            round_number=1,
            machine="1호기",
            numbers=[1, 2, 3, 4, 5],
            odd_even_ratio="3:2",
            high_low_ratio="2:3",
            ac_value=4,
            tail_sum=15,
            total_sum=15,
        )


def test_validation_rejects_out_of_range():
    """LotteryDraw rejects numbers outside 1-45."""
    with pytest.raises(ValidationError, match="Numbers must be 1-45"):
        LotteryDraw(
            round_number=1,
            machine="1호기",
            numbers=[1, 2, 3, 4, 5, 46],
            odd_even_ratio="3:3",
            high_low_ratio="2:4",
            ac_value=5,
            tail_sum=21,
            total_sum=61,
        )


def test_validation_rejects_unsorted():
    """LotteryDraw rejects unsorted numbers."""
    with pytest.raises(ValidationError, match="sorted ascending"):
        LotteryDraw(
            round_number=1,
            machine="1호기",
            numbers=[5, 3, 10, 20, 30, 40],
            odd_even_ratio="3:3",
            high_low_ratio="3:3",
            ac_value=5,
            tail_sum=18,
            total_sum=108,
        )
