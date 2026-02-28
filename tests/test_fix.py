import pandas as pd

df = pd.read_excel("data/operations.xlsx")
df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

# Тест: транзакции за декабрь 2021
dec_2021 = df[(df["Дата операции"].dt.year == 2021) & (df["Дата операции"].dt.month == 12)]

print(f"Всего транзакций за декабрь 2021: {len(dec_2021)}")
print(f"Траты в Супермаркетах: {dec_2021[dec_2021['Категория'] == 'Супермаркеты']['Сумма операции'].sum()}")
