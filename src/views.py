"""Модуль для генерации JSON-ответов для веб-страниц."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from .utils import get_currency_rates, get_stock_prices, load_user_settings, parse_date_string

logger = logging.getLogger(__name__)


def get_greeting(date: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = date.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def calculate_card_stats(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Рассчитывает статистику по картам."""
    cards_data: List[Dict[str, Any]] = []

    if "Номер карты" in df.columns and "Сумма платежа" in df.columns:
        grouped = df.groupby("Номер карты")["Сумма платежа"].sum()
        for card, total in grouped.items():
            cards_data.append(
                {
                    "last_digits": str(card)[-4:],
                    "total_spent": round(float(total), 2),
                    "cashback": round(float(total) * 0.01, 2),
                }
            )
    return cards_data


def get_top_transactions(df: pd.DataFrame, n: int = 5) -> List[Dict[str, Any]]:
    """Возвращает топ-N транзакций по сумме."""
    if "Сумма платежа" not in df.columns:
        return []

    df_sorted = df.reindex(df["Сумма платежа"].abs().sort_values(ascending=False).index)
    top_df = df_sorted.head(n)

    result: List[Dict[str, Any]] = []
    for _, row in top_df.iterrows():
        date_val = row.get("Дата операции", "")
        if isinstance(date_val, pd.Timestamp):
            date_str = date_val.strftime("%d.%m.%Y")
        else:
            date_str = str(date_val)

        result.append(
            {
                "date": date_str,
                "amount": float(row["Сумма платежа"]),
                "category": row.get("Категория", "Unknown"),
                "description": row.get("Описание", ""),
            }
        )
    return result


def main_page_view(date_str: str) -> str:
    """
    Главная функция для страницы «Главная».

    Принимает дату и возвращает JSON со статистикой.
    """
    logger.info(f"Генерация главной страницы для даты: {date_str}")

    target_date = parse_date_string(date_str)
    if not target_date:
        return json.dumps({"error": "Invalid date format"}, ensure_ascii=False)

    from .main import get_current_transactions

    df = get_current_transactions()

    if not df.empty and "Дата операции" in df.columns:
        df = df.copy()
        df["Дата операции"] = pd.to_datetime(df["Дата операции"])
        start_of_month = target_date.replace(day=1, hour=0, minute=0, second=0)
        mask = (df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= target_date)
        df = df.loc[mask]

    settings = load_user_settings()

    response: Dict[str, Any] = {
        "greeting": get_greeting(target_date),
        "cards": calculate_card_stats(df),
        "top_transactions": get_top_transactions(df),
        "currency_rates": get_currency_rates(settings["user_currencies"]),
        "stock_prices": get_stock_prices(settings["user_stocks"]),
    }

    return json.dumps(response, ensure_ascii=False, indent=2)
