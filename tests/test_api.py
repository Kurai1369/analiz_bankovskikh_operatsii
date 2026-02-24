import requests

api_key = "3emvo6eHzKSpONvKjbLl1uyMgY14i0is"
url = "https://api.apilayer.com/exchangerates_data/latest"
params = {"base": "RUB", "symbols": "USD,EUR"}
headers = {"apikey": api_key}

response = requests.get(url, params=params, headers=headers)
print(response.json())
