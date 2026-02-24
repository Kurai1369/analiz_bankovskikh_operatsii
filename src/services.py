"""Модуль с бизнес-логикой сервисов."""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Сервис «Инвесткопилка».

    Рассчитывает сумму, которую можно отложить при округлении трат.

    Args:
        month: Месяц в формате 'YYYY-MM'.
        transactions: Список словарей с транзакциями.
        limit: Шаг округления (например, 10, 50, 100).

    Returns:
        Сумма накоплений.
    """
    logger.info(f"Расчет инвесткопилки за {month} с лимитом {limit}")
    total_saved = 0.0

    target_year, target_month = map(int, month.split("-"))

    for transaction in transactions:
        # Парсинг даты из строки 'YYYY-MM-DD'
        try:
            t_date = datetime.strptime(transaction.get("Дата операции", ""), "%Y-%m-%d")
        except (ValueError, TypeError):
            continue

        if t_date.year == target_year and t_date.month == target_month:
            amount = transaction.get("Сумма операции", 0)
            if isinstance(amount, (int, float)) and amount > 0:
                # Округление вверх до кратного limit
                import math

                rounded = math.ceil(amount / limit) * limit
                diff = rounded - amount
                total_saved += diff

    logger.info(f"Итого накоплено: {total_saved}")
    return round(total_saved, 2)


def profitable_cashback_categories(year: int, month: int, transactions: List[Dict[str, Any]]) -> str:
    """
    Сервис «Выгодные категории повышенного кешбэка».

    Анализирует, сколько можно заработать на каждой категории.
    """
    logger.info(f"Анализ выгодных категорий за {year}-{month}")
    category_sums: Dict[str, float] = {}

    for t in transactions:
        try:
            t_date = datetime.strptime(t.get("Дата операции", ""), "%Y-%m-%d")
            if t_date.year == year and t_date.month == month:
                cat = t.get("Категория", "Прочее")
                amount = abs(t.get("Сумма операции", 0))
                category_sums[cat] = category_sums.get(cat, 0) + amount
        except (ValueError, TypeError):
            continue

    # Расчет потенциального кешбэка (условно 5% для примера)
    result = {cat: round(sum_val * 0.05, 2) for cat, sum_val in category_sums.items()}
    return json.dumps(result, ensure_ascii=False)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> str:
    """Сервис «Простой поиск»."""
    logger.info(f"Поиск по запросу: {query}")
    found = []
    query_lower = query.lower()

    for t in transactions:
        desc = str(t.get("Описание", "")).lower()
        cat = str(t.get("Категория", "")).lower()
        if query_lower in desc or query_lower in cat:
            found.append(t)

    return json.dumps(found, ensure_ascii=False)


def search_phone_numbers(transactions: List[Dict[str, Any]]) -> str:
    """Сервис «Поиск по телефонным номерам»."""
    logger.info("Поиск телефонных номеров")
    # Гибкий паттерн: принимает 2-3 цифры в третьей группе
    pattern = re.compile(r"\+7[\s\-]?\d{3}[\s\-]?\d{2,3}[\s\-]?\d{2}[\s\-]?\d{2}")
    found = []

    for t in transactions:
        desc = str(t.get("Описание", ""))
        if pattern.search(desc):
            found.append(t)

    return json.dumps(found, ensure_ascii=False)


def search_transfers_to_individuals(transactions: List[Dict[str, Any]]) -> str:
    """Сервис «Поиск переводов физическим лицам»."""
    logger.info("Поиск переводов физлицам")
    # Имя и первая буква фамилии: Кириллица, пробел, Заглавная буква, точка
    pattern = re.compile(r"[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.")
    found = []

    for t in transactions:
        if t.get("Категория") == "Переводы":
            desc = str(t.get("Описание", ""))
            if pattern.search(desc):
                found.append(t)

    return json.dumps(found, ensure_ascii=False)
