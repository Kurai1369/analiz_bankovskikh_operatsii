"""Точка входа в приложение."""

import os
import sys
from pathlib import Path
from typing import Any, Optional, cast

import pandas as pd

# --- Блок для корректного запуска как скрипта ---
# Добавляем корневую папку проекта в sys.path, чтобы работали импорты пакета src
if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

# --- Импорты пакета ---
from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import load_transactions, logger
from src.views import main_page_view

# Глобальная переменная для доступа к данным в модулях
_current_df: Optional[pd.DataFrame] = None


def get_current_transactions() -> pd.DataFrame:
    """Возвращает текущий загруженный DataFrame."""
    global _current_df
    if _current_df is None:
        _current_df = pd.DataFrame()
    return _current_df


def main() -> None:
    """Запуск всех реализованных функциональностей."""
    global _current_df

    logger.info("Запуск приложения")

    data_path = os.path.join("data", "operations.xlsx")
    if not os.path.exists(data_path):
        logger.warning(f"Файл {data_path} не найден. Создаем пустой DataFrame.")
        _current_df = pd.DataFrame(columns=["Дата операции", "Сумма платежа", "Категория", "Описание", "Номер карты"])
    else:
        _current_df = load_transactions(data_path)

    print("--- Главная страница ---")
    json_response = main_page_view("2023-10-15 12:00:00")
    print(json_response)

    print("\n--- Инвесткопилка ---")
    # Исправление типа для mypy
    transactions_list: list[dict[str, Any]] = (
        cast(list[dict[str, Any]], _current_df.to_dict(orient="records")) if not _current_df.empty else []
    )
    saved_amount = investment_bank("2023-10", transactions_list, 50)
    print(f"Накоплено: {saved_amount}")

    print("\n--- Отчет: Траты по категории ---")
    if not _current_df.empty:
        report_df = spending_by_category(_current_df, "Супермаркеты", "2023-10-15")
        print(report_df)
    else:
        print("Нет данных для отчета")

    logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()
