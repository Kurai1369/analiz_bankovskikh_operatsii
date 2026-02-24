"""Модуль для формирования отчетов."""

import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def _filter_by_date_range(df: pd.DataFrame, date: Optional[str] = None, days: int = 90) -> pd.DataFrame:
    """
    Вспомогательная функция: фильтрует DataFrame по диапазону дат.

    Args:
        df: Исходный DataFrame с колонкой "Дата операции".
        date: Конечная дата в формате YYYY-MM-DD (по умолчанию — сегодня).
        days: Количество дней для диапазона (по умолчанию 90).

    Returns:
        Отфильтрованный DataFrame.
    """
    if df.empty or "Дата операции" not in df.columns:
        return pd.DataFrame()

    result = df.copy()

    # Парсинг конечной даты
    if date:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=days)

    # Конвертация и фильтрация
    result["Дата операции"] = pd.to_datetime(result["Дата операции"], dayfirst=True, errors="coerce")
    mask = (result["Дата операции"] >= start_date) & (result["Дата операции"] <= end_date)

    return result.loc[mask].copy()


def save_report(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для сохранения результата отчета в файл.

    Args:
        filename: Имя файла. Если None, используется default_report.json.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            target_file = filename if filename else "default_report.json"

            # Конвертация результата в JSON
            if isinstance(result, pd.DataFrame):
                json_data = result.to_json(orient="records", force_ascii=False)
            elif isinstance(result, dict):
                json_data = json.dumps(result, force_ascii=False)
            else:
                json_data = str(result)

            try:
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(json_data)
                logger.info(f"Отчет сохранен в {target_file}")
            except Exception as e:
                logger.error(f"Ошибка сохранения отчета: {e}")

            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Отчет «Траты по категории».

    Возвращает траты по заданной категории за последние 3 месяца.
    """
    logger.info(f"Формирование отчета по категории: {category}")

    # Фильтрация по дате
    df_filtered = _filter_by_date_range(transactions, date, days=90)
    if df_filtered.empty:
        return pd.DataFrame()

    # Фильтрация по категории
    if "Категория" not in df_filtered.columns:
        return pd.DataFrame()

    df_cat = df_filtered[df_filtered["Категория"] == category]

    if df_cat.empty or "Сумма платежа" not in df_cat.columns:
        return pd.DataFrame()

    # Группировка по дням
    report = df_cat.groupby(df_cat["Дата операции"].dt.date)["Сумма платежа"].sum().reset_index()
    report.columns = ["Дата", "Сумма"]

    return report


@save_report("weekday_report.json")
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Отчет «Траты по дням недели»."""
    logger.info("Формирование отчета по дням недели")

    # Фильтрация по дате
    df_filtered = _filter_by_date_range(transactions, date, days=90)
    if df_filtered.empty or "Сумма платежа" not in df_filtered.columns:
        return pd.DataFrame(columns=["День", "Среднее"])

    # Группировка по дню недели
    df_filtered["weekday"] = df_filtered["Дата операции"].dt.day_name()
    result = df_filtered.groupby("weekday")["Сумма платежа"].mean().round(2).reset_index()
    result.columns = ["День", "Среднее"]

    return result


@save_report("workday_report.json")
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Отчет «Траты в рабочий/выходной день»."""
    logger.info("Формирование отчета рабочий/выходной")

    # Фильтрация по дате
    df_filtered = _filter_by_date_range(transactions, date, days=90)
    if df_filtered.empty or "Сумма платежа" not in df_filtered.columns:
        return pd.DataFrame(columns=["Тип дня", "Среднее"])

    # Разделение на рабочие/выходные
    df_filtered["is_weekend"] = df_filtered["Дата операции"].dt.dayofweek >= 5
    df_filtered["Тип дня"] = df_filtered["is_weekend"].map({True: "Выходной", False: "Рабочий"})

    result = df_filtered.groupby("Тип дня")["Сумма платежа"].mean().round(2).reset_index()

    return result
