"""Тесты для модуля views."""

import pandas as pd
import pytest

from src.views import main_page_view


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Фикстура с тестовым DataFrame."""
    return pd.DataFrame(
        {
            "Дата операции": ["2023-10-15 10:00:00", "2023-10-15 12:00:00", "2023-10-16 10:00:00"],
            "Сумма платежа": [100.0, 200.0, 300.0],
            "Категория": ["Супермаркеты", "Супермаркеты", "Кафе"],
        }
    )


def test_main_page_view_empty_df() -> None:
    """Тест с пустым DataFrame."""
    empty_df = pd.DataFrame()
    result = main_page_view("2023-10-15 12:00:00", empty_df)
    assert result["error"] == "Нет данных для отображения"


def test_main_page_view_with_data(sample_df: pd.DataFrame) -> None:
    """Тест с данными."""
    result = main_page_view("2023-10-15 12:00:00", sample_df)
    assert result["status"] == "ok"
    assert result["transactions_count"] == 2  # Только 2 транзакции за 15 октября
    assert result["total_spent"] == 300.0


def test_main_page_view_invalid_date(sample_df: pd.DataFrame) -> None:
    """Тест с некорректной датой."""
    result = main_page_view("invalid-date", sample_df)
    assert result["status"] == "fail"
    assert "error" in result
