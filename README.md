# Анализатор транзакций

Приложение для анализа банковских транзакций.

### 📁 Структура проекта
```
shop_project/
├── data/
│ └── operations.xlsx
├── src/
│ ├── __init__.py
│ ├── main.py
│ ├── reports.py
│ ├── services.py
│ ├── utils.py
│ └── views.py
├── tests/
│ ├── __init__.py
│ ├── conftest.py
│ ├── test_api.py
│ ├── test_fix.py
│ ├── test_main.py
│ ├── test_reports.py
│ ├── test_services.py
│ ├── test_utils.py
│ └── test_views.py
├── .env_template
├── .gitignore
├── app.log
├── .flake8
├── main.py
├── pyproject.toml
└── README.md
```

## Установка
1. `poetry install`
2. Заполнить `.env`
3. Положить файл `operations.xlsx` в папку `data`

## Запуск
`poetry run python src/main.py`

## Тесты
`poetry run pytest`
