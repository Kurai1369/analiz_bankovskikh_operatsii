"""Точка входа в приложение."""

import os
import sys
from pathlib import Path
from typing import Any, Optional, cast

import pandas as pd

# --- Блок для запуска как скрипта ---
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


def get_current_transactions(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Возвращает переданный DataFrame или пустой, если None."""
    return df if df is not None else pd.DataFrame()


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

    # Даты для разных функций
    main_page_date = "2021-12-15 12:00:00"  # для main_page_view — с временем
    investment_month = "2021-12"  # для investment_bank — только месяц
    category_report_date = "2021-12-15"  # для spending_by_category — только дата

    print("--- Главная страница ---")
    # Передаём DataFrame и дату
    json_response = main_page_view(main_page_date, _current_df)
    print(json_response)

    print("\n--- Инвесткопилка ---")
    transactions_list: list[dict[str, Any]] = (
        cast(list[dict[str, Any]], _current_df.to_dict(orient="records")) if not _current_df.empty else []
    )
    saved_amount = investment_bank(investment_month, transactions_list, 50)
    print(f"Накоплено: {saved_amount}")

    print("\n--- Отчет: Траты по категории ---")
    if not _current_df.empty:
        report_df = spending_by_category(_current_df, "Супермаркеты", category_report_date)
        print(report_df)
    else:
        print("Нет данных для отчета")

    logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()
