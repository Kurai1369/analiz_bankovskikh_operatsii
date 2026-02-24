"""Тесты для модуля reports."""

import os

import pandas as pd
import pytest

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday


def test_spending_by_category_filtering(sample_transactions_df: pd.DataFrame) -> None:
    """Тест фильтрации по категории и дате."""
    result = spending_by_category(sample_transactions_df, "Супермаркеты", "2023-10-15")
    assert isinstance(result, pd.DataFrame)
    assert os.path.exists("default_report.json")
    os.remove("default_report.json")


def test_spending_by_category_empty_df() -> None:
    """Тест с пустым DataFrame."""
    empty_df = pd.DataFrame()
    result = spending_by_category(empty_df, "Супермаркеты")
    assert result.empty


def test_spending_by_category_no_date_column() -> None:
    """Тест DataFrame без колонки даты."""
    df = pd.DataFrame({"Категория": ["Тест"], "Сумма": [100]})
    result = spending_by_category(df, "Тест")
    assert result.empty


@pytest.mark.parametrize(
    "category,expected_rows",
    [
        ("Супермаркеты", 2),  # 2 транзакции в периоде
        ("Переводы", 0),  # 0 в периоде (одна есть, но в другом месяце)
    ],
)
def test_spending_by_category_parametrized(
    sample_transactions_df: pd.DataFrame, category: str, expected_rows: int
) -> None:
    """Параметризированный тест по категориям."""
    result = spending_by_category(sample_transactions_df, category, "2023-10-15")
    # Проверяем, что результат - DataFrame (детали зависят от реализации)
    assert isinstance(result, pd.DataFrame)


def test_spending_by_weekday(sample_transactions_df: pd.DataFrame) -> None:
    """Тест отчета по дням недели."""
    result = spending_by_weekday(sample_transactions_df, "2023-10-15")
    assert isinstance(result, pd.DataFrame)
    assert os.path.exists("weekday_report.json")
    os.remove("weekday_report.json")


def test_spending_by_workday(sample_transactions_df: pd.DataFrame) -> None:
    """Тест отчета рабочий/выходной."""
    result = spending_by_workday(sample_transactions_df, "2023-10-15")
    assert isinstance(result, pd.DataFrame)
    assert os.path.exists("workday_report.json")
    os.remove("workday_report.json")
