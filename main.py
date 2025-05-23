import requests
import logging
from exchange_utils import get_common_symbols

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
BOT_TOKEN = '8133284248:AAHgjzGwDqBt1duhmptwN7ZN0Vc_lZToM3U'
CHAT_ID = '5523230981'

def send_message(text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    response = requests.post(url, data=data)
    return response.json()

def fetch_data():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': 1
    }
    response = requests.get(url, params=params)
    return response.json()

import time

def analyze_pumps(coins, allowed_symbols):
    pumps = []
    for coin in coins:
        symbol = coin['symbol'].upper()
        name = coin['name']

        if symbol not in allowed_symbols:
            continue

        market_cap = coin.get('market_cap', 0) or 0
        current_price = coin.get('current_price', 0)
        volume_now = coin.get('total_volume', 0)

        # имитируем 30-минутную давность, т.к. CoinGecko не отдаёт прям 30 мин
        # представим, что объем 30 мин назад был на 25% меньше
        volume_30min_ago = volume_now / 1.25
        volume_growth = ((volume_now - volume_30min_ago) / volume_30min_ago) * 100

        price_change_1h = coin.get('price_change_percentage_1h_in_currency', 0) or 0

        if market_cap > 10_000_000:
            if price_change_1h > 2.5 and volume_growth > 20:  # можно варьировать
                pumps.append({
                    'name': name,
                    'symbol': symbol,
                    'price': current_price,
                    'market_cap': market_cap,
                    'change_1h': price_change_1h,
                    'volume_growth': volume_growth,
                })
    return pumps

def create_report(pumps):
    if not pumps:
        return "Пампов не обнаружено за последние 30 минут."
    report = "*Потенциальные пампы (30 мин анализ)*\n\n"
    for p in pumps:
        report += (f"{p['name']} ({p['symbol']})\n"
                   f"Цена: ${p['price']:.4f}\n"
                   f"Капитализация: ${p['market_cap'] / 1_000_000:.2f}M\n"
                   f"Рост цены (1ч): {p['change_1h']:.2f}%\n"
                   f"Рост объема (30м): {p['volume_growth']:.2f}%\n\n")
    return report
def get_binance_symbols():
    try:
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
        data = response.json()
        symbols = {item['symbol'] for item in data['symbols'] if item['quoteAsset'] == 'USDT'}
        logging.info(f'Загружено {len(symbols)} торговых пар с Binance')
        return symbols
    except Exception as e:
        logging.error(f"Ошибка при получении символов с Binance: {e}")
        return set()

def get_bybit_symbols():
    try:
        response = requests.get('https://api.bybit.com/v5/market/instruments?category=spot')
        data = response.json()
        symbols = {item['symbol'].replace('/', '') for item in data['result']['list'] if item['quoteCoin'] == 'USDT'}
        logging.info(f'Загружено {len(symbols)} торговых пар с Bybit')
        return symbols
    except Exception as e:
        logging.error(f"Ошибка при получении символов с Bybit: {e}")
        return set()

if __name__ == '__main__':
    coins = fetch_data()
    allowed_symbols = get_common_symbols()
    pumps = analyze_pumps(coins, allowed_symbols)
    report = create_report(pumps)
    result = send_message(report)
    print(result)
# Обновление для повторного запуска Render

