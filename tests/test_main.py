"""Тесты для модуля main."""

from src.main import get_current_transactions, main


def test_get_current_transactions_empty() -> None:
    """Тест получения пустого DataFrame."""
    result = get_current_transactions()
    assert result is not None


def test_main_execution(mocker) -> None:
    """Тест запуска main функции."""
    mocker.patch("src.main.load_transactions", return_value=mocker.Mock())
    mocker.patch("src.main.main_page_view", return_value="{}")
    mocker.patch("src.main.investment_bank", return_value=0.0)
    mocker.patch("src.main.spending_by_category", return_value=mocker.Mock())
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("src.main._current_df", None)

    # main() не должен выбрасывать исключений
    main()
