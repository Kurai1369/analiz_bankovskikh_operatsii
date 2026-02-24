"""Вспомогательные функции для загрузки данных, логирования и API."""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

# Конфигурация API из переменных окружения
EXCHANGERATES_API_KEY = os.getenv("EXCHANGERATES_API_KEY", "")
EXCHANGERATES_BASE_URL = os.getenv("EXCHANGERATES_BASE_URL", "https://api.apilayer.com/exchangerates_data")
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")
ALPHAVANTAGE_BASE_URL = os.getenv("ALPHAVANTAGE_BASE_URL", "https://www.alphavantage.co/query")


def load_transactions(file_path: str) -> pd.DataFrame:
    """Загружает транзакции из Excel файла в DataFrame."""
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Загружено {len(df)} транзакций из {file_path}")
        return df
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла: {e}")
        return pd.DataFrame()


def load_user_settings(path: str = "user_settings.json") -> dict[str, Any]:
    """Загружает пользовательские настройки из JSON."""
    default_settings: dict[str, Any] = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                return data
        except json.JSONDecodeError:
            logger.warning("Ошибка в user_settings.json, используются настройки по умолчанию")
    return default_settings


def get_currency_rates(currencies: List[str], base: str = "RUB") -> List[Dict[str, Any]]:
    """
    Получает курсы валют через Exchangerates API.

    Args:
        currencies: Список кодов валют (например, ["USD", "EUR"]).
        base: Базовая валюта (по умолчанию RUB).

    Returns:
        Список словарей с курсами валют.
    """
    if not EXCHANGERATES_API_KEY:
        logger.warning("API ключ для курсов валют не настроен")
        return [{"currency": c, "rate": 0.0} for c in currencies]

    logger.info(f"Запрос курсов валют для: {currencies} (base: {base})")

    try:
        url = f"{EXCHANGERATES_BASE_URL}/live"
        params = {
            "base": base,
            "symbols": ",".join(currencies),
        }
        headers = {
            "apikey": EXCHANGERATES_API_KEY,
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            logger.error(f"API вернул ошибку: {data}")
            return [{"currency": c, "rate": 0.0} for c in currencies]

        rates = data.get("quotes", {})
        result = []
        for currency in currencies:
            # Ключ в ответе имеет формат BASECURRENCY, например RUBUSD
            key = f"{base}{currency}"
            rate = rates.get(key, 0.0)
            result.append({"currency": currency, "rate": round(rate, 2)})
            logger.debug(f"Курс {currency}: {rate}")

        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса к API валют: {e}")
        return [{"currency": c, "rate": 0.0} for c in currencies]
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при получении курсов: {e}")
        return [{"currency": c, "rate": 0.0} for c in currencies]


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает цены акций через Alpha Vantage API.

    Args:
        stocks: Список тикеров акций (например, ["AAPL", "TSLA"]).

    Returns:
        Список словарей с ценами акций.
    """
    if not ALPHAVANTAGE_API_KEY:
        logger.warning("API ключ для акций не настроен")
        return [{"stock": s, "price": 0.0} for s in stocks]

    logger.info(f"Запрос цен акций для: {stocks}")
    result = []

    for stock in stocks:
        try:
            # Alpha Vantage имеет лимит 5 запросов в минуту для бесплатного тарифа
            time.sleep(12)  # Небольшая задержка между запросами

            url = ALPHAVANTAGE_BASE_URL
            params = {
                "function": "GLOBAL_QUOTE",  # Быстрый эндпоинт для текущей цены
                "symbol": stock,
                "apikey": ALPHAVANTAGE_API_KEY,
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Парсинг ответа GLOBAL_QUOTE
            quote = data.get("Global Quote", {})
            price_str = quote.get("05. price")

            if price_str:
                price = float(price_str)
                result.append({"stock": stock, "price": round(price, 2)})
                logger.debug(f"Цена {stock}: {price}")
            else:
                logger.warning(f"Не удалось получить цену для {stock}: {data}")
                result.append({"stock": stock, "price": 0.0})

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к API акций для {stock}: {e}")
            result.append({"stock": stock, "price": 0.0})
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при получении цены {stock}: {e}")
            result.append({"stock": stock, "price": 0.0})

    return result


def parse_date_string(date_str: str) -> Optional[datetime]:
    """Парсит строку даты в объект datetime."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.error(f"Неверный формат даты: {date_str}")
        return None
