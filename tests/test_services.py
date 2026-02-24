"""Тесты для модуля services."""

import json

import pytest

from src.services import (
    investment_bank,
    profitable_cashback_categories,
    search_phone_numbers,
    search_transfers_to_individuals,
    simple_search,
)


def test_investment_bank_calculation(sample_transactions_list: list[dict[str, any]]) -> None:
    """Тест расчёта инвесткопилки."""
    result = investment_bank("2023-10", sample_transactions_list, 50)
    assert isinstance(result, float)
    assert result >= 0


def test_investment_bank_empty_list() -> None:
    """Тест с пустым списком транзакций."""
    result = investment_bank("2023-10", [], 50)
    assert result == 0.0


def test_investment_bank_invalid_date_format() -> None:
    """Тест с некорректным форматом даты в транзакции."""
    transactions = [{"Дата операции": "invalid", "Сумма операции": 100}]
    result = investment_bank("2023-10", transactions, 50)
    assert result == 0.0


def test_profitable_cashback_categories(sample_transactions_list: list[dict[str, any]]) -> None:
    """Тест анализа выгодных категорий кешбэка."""
    result_str = profitable_cashback_categories(2023, 10, sample_transactions_list)
    result = json.loads(result_str)
    assert isinstance(result, dict)


def test_profitable_cashback_categories_empty() -> None:
    """Тест с пустыми данными."""
    result = profitable_cashback_categories(2023, 10, [])
    assert json.loads(result) == {}


def test_simple_search_found(sample_transactions_list: list[dict[str, any]]) -> None:
    """Тест простого поиска — найдено."""
    # Добавим описание для поиска
    transactions = [{"Описание": "Магнит продукты", "Категория": "Супермаркеты"}]
    result_str = simple_search("Магнит", transactions)
    result = json.loads(result_str)
    assert len(result) == 1


def test_simple_search_not_found() -> None:
    """Тест простого поиска — не найдено."""
    transactions = [{"Описание": "Пятерочка", "Категория": "Супермаркеты"}]
    result_str = simple_search("Магнит", transactions)
    assert json.loads(result_str) == []


@pytest.mark.parametrize(
    "description,should_match",
    [
        ("+7 921 111-22-33", True),
        ("+79955555555", True),
        ("+7 995 555-55-55", True),
        ("Нет телефона", False),
        ("+1 234 567-89-00", False),
    ],
)
def test_search_phone_numbers_parametrized(description: str, should_match: bool) -> None:
    """Параметризированный тест поиска телефонов."""
    transactions = [{"Описание": description}]
    result_str = search_phone_numbers(transactions)
    result = json.loads(result_str)
    if should_match:
        assert len(result) == 1
    else:
        assert len(result) == 0


@pytest.mark.parametrize(
    "category, description, should_match",
    [
        ("Переводы", "Иван И.", True),
        ("Переводы", "Мария П.", True),
        ("Переводы", "Без фамилии", False),
        ("Супермаркеты", "Иван И.", False),  # не та категория
    ],
)
def test_search_transfers_parametrized(category: str, description: str, should_match: bool) -> None:
    """Параметризированный тест поиска переводов физлицам."""
    transactions = [{"Категория": category, "Описание": description}]
    result_str = search_transfers_to_individuals(transactions)
    result = json.loads(result_str)
    if should_match:
        assert len(result) == 1
    else:
        assert len(result) == 0
