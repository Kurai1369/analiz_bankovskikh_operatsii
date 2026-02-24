"""Фикстуры для тестов."""

import pandas as pd
import pytest
import requests


@pytest.fixture
def sample_transactions_df() -> pd.DataFrame:
    """Фикстура с тестовым DataFrame."""
    data = {
        "Дата операции": ["2023-10-01", "2023-10-05", "2023-10-10", "2023-09-01"],
        "Сумма платежа": [100.5, 200.0, -50.0, 1000.0],
        "Категория": ["Супермаркеты", "Супермаркеты", "Переводы", "Супермаркеты"],
        "Описание": ["Магнит", "Пятерочка", "Иван И.", "Ашан"],
        "Номер карты": [1234, 1234, 5678, 1234],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_transactions_list() -> list[dict[str, any]]:
    """Фикстура с тестовым списком словарей."""
    return [
        {"Дата операции": "2023-10-01", "Сумма операции": 100.5},
        {"Дата операции": "2023-10-05", "Сумма операции": 120.0},
        {"Дата операции": "2023-11-01", "Сумма операции": 50.0},
    ]


@pytest.fixture
def mock_currency_api_success(mocker):
    """Мокирование успешного ответа API валют."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "success": True,
        "quotes": {
            "RUBUSD": 0.011,
            "RUBEUR": 0.010,
        },
    }
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


@pytest.fixture
def mock_stock_api_success(mocker):
    """Мокирование успешного ответа API акций."""

    def mock_get(*args, **kwargs):
        symbol = kwargs.get("params", {}).get("symbol", "AAPL")
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"Global Quote": {"05. price": "150.25" if symbol == "AAPL" else "200.50"}}
        mock_response.raise_for_status = mocker.Mock()
        return mock_response

    mocker.patch("requests.get", side_effect=mock_get)
    return mocker.patch("time.sleep")


@pytest.fixture
def mock_api_failure(mocker):
    """Мокирование ошибки API."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("API Error"))
    return mocker.patch("time.sleep")
