"""Тесты для модуля views."""

import json
from datetime import datetime

import pandas as pd
import pytest

from src.views import calculate_card_stats, get_greeting, get_top_transactions, main_page_view


@pytest.mark.parametrize(
    "hour,expected",
    [
        (8, "Доброе утро"),
        (14, "Добрый день"),
        (20, "Добрый вечер"),
        (2, "Доброй ночи"),
    ],
)
def test_get_greeting_parametrized(hour: int, expected: str) -> None:
    """Параметризированный тест приветствий."""
    date = datetime(2023, 1, 1, hour, 0, 0)
    assert get_greeting(date) == expected


def test_calculate_card_stats_empty() -> None:
    """Тест статистики карт с пустым DF."""
    result = calculate_card_stats(pd.DataFrame())
    assert result == []


def test_calculate_card_stats_with_data() -> None:
    """Тест статистики карт с данными."""
    df = pd.DataFrame({"Номер карты": [1234, 1234, 5678], "Сумма платежа": [100.0, 200.0, 50.0]})
    result = calculate_card_stats(df)
    assert len(result) == 2
    assert result[0]["last_digits"] == "1234"
    assert result[0]["total_spent"] == 300.0
    assert result[0]["cashback"] == 3.0


def test_get_top_transactions_empty() -> None:
    """Тест топ-транзакций с пустым DF."""
    result = get_top_transactions(pd.DataFrame())
    assert result == []


def test_main_page_view_invalid_date() -> None:
    """Тест главной страницы с неверной датой."""
    result = json.loads(main_page_view("invalid-date"))
    assert "error" in result


def test_main_page_view_structure(mocker, sample_transactions_df: pd.DataFrame) -> None:
    """Тест структуры ответа главной страницы."""
    mocker.patch("src.main.get_current_transactions", return_value=sample_transactions_df)
    mocker.patch("src.views.get_currency_rates", return_value=[{"currency": "USD", "rate": 90}])
    mocker.patch("src.views.get_stock_prices", return_value=[{"stock": "AAPL", "price": 150}])

    result_str = main_page_view("2023-10-15 12:00:00")
    result = json.loads(result_str)

    assert "greeting" in result
    assert "cards" in result
    assert "currency_rates" in result
