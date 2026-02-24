"""Дополнительные тесты для модуля utils."""

import json

import pytest
import requests

from src.utils import get_currency_rates, get_stock_prices, load_transactions, load_user_settings, parse_date_string


def test_load_transactions_file_not_found() -> None:
    """Тест загрузки несуществующего файла."""
    result = load_transactions("nonexistent_file.xlsx")
    assert result.empty


def test_load_user_settings_default() -> None:
    """Тест загрузки настроек по умолчанию (файл не существует)."""
    result = load_user_settings("nonexistent.json")
    assert "user_currencies" in result
    assert "user_stocks" in result


def test_load_user_settings_valid_file(tmp_path) -> None:
    """Тест загрузки валидных настроек из файла."""
    settings_file = tmp_path / "settings.json"
    settings = {"user_currencies": ["GBP"], "user_stocks": ["NVDA"]}
    settings_file.write_text(json.dumps(settings), encoding="utf-8")

    result = load_user_settings(str(settings_file))
    assert result["user_currencies"] == ["GBP"]


def test_load_user_settings_invalid_json(tmp_path) -> None:
    """Тест обработки невалидного JSON в настройках."""
    settings_file = tmp_path / "bad.json"
    settings_file.write_text("{ invalid json }", encoding="utf-8")

    result = load_user_settings(str(settings_file))
    assert "user_currencies" in result


@pytest.mark.parametrize("date_str,expected", [
    ("2023-10-15 12:30:45", "2023-10-15 12:30:45"),
    ("invalid", None),
    ("", None),
])
def test_parse_date_string_parametrized(date_str: str, expected: str | None) -> None:
    """Параметризированный тест парсинга дат."""
    result = parse_date_string(date_str)
    if expected is None:
        assert result is None
    else:
        assert result is not None
        assert result.strftime("%Y-%m-%d %H:%M:%S") == expected


def test_get_currency_rates_no_api_key(mocker) -> None:
    """Тест получения курсов без API ключа."""
    mocker.patch("src.utils.EXCHANGERATES_API_KEY", "")
    result = get_currency_rates(["USD"])
    assert len(result) == 1
    assert result[0]["rate"] == 0.0


def test_get_currency_rates_api_error(mocker) -> None:
    """Тест обработки ошибки запроса к API валют."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Network error"))
    result = get_currency_rates(["USD"])
    assert len(result) == 1
    assert result[0]["rate"] == 0.0


def test_get_stock_prices_no_api_key(mocker) -> None:
    """Тест получения цен акций без API ключа."""
    mocker.patch("src.utils.ALPHAVANTAGE_API_KEY", "")
    result = get_stock_prices(["AAPL"])
    assert len(result) == 1
    assert result[0]["price"] == 0.0


def test_get_stock_prices_api_error(mocker) -> None:
    """Тест обработки ошибки запроса к API акций."""
    def mock_get(*args, **kwargs):
        raise requests.exceptions.RequestException("API Error")

    mocker.patch("requests.get", side_effect=mock_get)
    mocker.patch("time.sleep")
    result = get_stock_prices(["AAPL"])
    assert len(result) == 1
    assert result[0]["price"] == 0.0


def test_get_stock_prices_invalid_response(mocker) -> None:
    """Тест обработки невалидного ответа API акций."""
    def mock_get(*args, **kwargs):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"Global Quote": {}}
        mock_response.raise_for_status = mocker.Mock()
        return mock_response

    mocker.patch("requests.get", side_effect=mock_get)
    mocker.patch("time.sleep")
    result = get_stock_prices(["AAPL"])
    assert result[0]["price"] == 0.0


def test_get_currency_rates_success(mocker) -> None:
    """Тест успешного получения курсов валют."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "success": True,
        "quotes": {"RUBUSD": 0.011, "RUBEUR": 0.010}
    }
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.get", return_value=mock_response)

    result = get_currency_rates(["USD", "EUR"])
    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert isinstance(result[0]["rate"], (int, float))


def test_get_stock_prices_success(mocker) -> None:
    """Тест успешного получения цен акций."""
    # Мокаем API-ключ, чтобы функция не возвращалась рано
    mocker.patch("src.utils.ALPHAVANTAGE_API_KEY", "test_key")

    def mock_get(*args, **kwargs):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"Global Quote": {"05. price": "150.25"}}
        mock_response.raise_for_status = mocker.Mock()
        return mock_response

    mocker.patch("requests.get", side_effect=mock_get)
    mocker.patch("time.sleep")

    result = get_stock_prices(["AAPL"])
    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.25


def test_get_currency_rates_api_failure_with_response(mocker) -> None:
    """Тест обработки ответа API с success=False."""
    mocker.patch("src.utils.EXCHANGERATES_API_KEY", "test_key")

    mock_response = mocker.Mock()
    mock_response.json.return_value = {"success": False, "error": {"code": 401}}
    mock_response.raise_for_status = mocker.Mock()
    mocker.patch("requests.get", return_value=mock_response)

    result = get_currency_rates(["USD"])
    assert len(result) == 1
    assert result[0]["rate"] == 0.0


def test_get_stock_prices_exception_handling(mocker) -> None:
    """Тест обработки исключения при запросе акций."""
    mocker.patch("src.utils.ALPHAVANTAGE_API_KEY", "test_key")
    mocker.patch("requests.get", side_effect=Exception("Unexpected error"))
    mocker.patch("time.sleep")

    result = get_stock_prices(["AAPL"])
    assert len(result) == 1
    assert result[0]["price"] == 0.0


def test_get_stock_prices_missing_price_field(mocker) -> None:
    """Тест ответа API без поля цены."""
    mocker.patch("src.utils.ALPHAVANTAGE_API_KEY", "test_key")

    def mock_get(*args, **kwargs):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"Global Quote": {}}  # Пустой объект
        mock_response.raise_for_status = mocker.Mock()
        return mock_response

    mocker.patch("requests.get", side_effect=mock_get)
    mocker.patch("time.sleep")

    result = get_stock_prices(["AAPL"])
    assert result[0]["price"] == 0.0
