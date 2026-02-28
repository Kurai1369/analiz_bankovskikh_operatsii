"""Модуль для генерации JSON-ответов для веб-страниц."""

import logging
from typing import Any

import pandas as pd

from .utils import get_currency_rates, get_stock_prices, load_user_settings

logger = logging.getLogger(__name__)


def main_page_view(date_str: str, df: pd.DataFrame) -> dict[str, Any]:
    """
    Формирует ответ главной страницы.

    Args:
        date_str: Дата для фильтрации в формате 'YYYY-MM-DD HH:MM:SS'
        df: DataFrame с транзакциями (передаётся явно)
    """
    if df.empty:
        return {"error": "Нет данных для отображения"}

    try:
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["Дата операции"]):
            df["Дата операции"] = pd.to_datetime(
                df["Дата операции"],
                format="%Y-%m-%d %H:%M:%S",  # явный формат
                errors="coerce"
            )

        target_date = pd.to_datetime(date_str.split()[0])
        filtered = df[df["Дата операции"].dt.date == target_date.date()]

        total_spent = float(filtered["Сумма платежа"].abs().sum()) if not filtered.empty else 0.0

        # Добавляем курсы валют и акции (как было в оригинале)
        settings = load_user_settings()

        return {
            "status": "ok",
            "date": date_str,
            "transactions_count": len(filtered),
            "total_spent": round(total_spent, 2),
            "categories": filtered["Категория"].value_counts().to_dict() if not filtered.empty else {},
            "currency_rates": get_currency_rates(settings["user_currencies"]),
            "stock_prices": get_stock_prices(settings["user_stocks"]),
        }
    except Exception as e:
        logger.error(f"Ошибка в main_page_view: {e}")
        return {"error": str(e), "status": "fail"}
