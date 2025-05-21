import requests

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
        'page': 1,
        'price_change_percentage': '1h,24h'
    }
    response = requests.get(url, params=params)
    return response.json()

def analyze_pumps(coins):
    pumps = []
    for coin in coins:
        market_cap = coin.get('market_cap', 0) or 0
        price_change_1h = coin.get('price_change_percentage_1h_in_currency', 0) or 0
        price_change_24h = coin.get('price_change_percentage_24h_in_currency', 0) or 0

        if market_cap > 10_000_000:
            if price_change_1h > 5 or price_change_24h > 15:
                pumps.append({
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'price': coin['current_price'],
                    'market_cap': market_cap,
                    'change_1h': price_change_1h,
                    'change_24h': price_change_24h,
                })
    return pumps

def create_report(pumps):
    if not pumps:
        return "Пампов не обнаружено за последние часы."
    report = "*Потенциальные пампы криптовалют*\n\n"
    for p in pumps:
        report += (f"{p['name']} ({p['symbol']})\n"
                   f"Цена: ${p['price']:.4f}\n"
                   f"Капитализация: ${p['market_cap'] / 1_000_000:.2f}M\n"
                   f"Рост за 1 час: {p['change_1h']:.2f}%\n"
                   f"Рост за 24 часа: {p['change_24h']:.2f}%\n\n")
    return report

if __name__ == '__main__':
    coins = fetch_data()
    pumps = analyze_pumps(coins)
    report = create_report(pumps)
    result = send_message(report)
    print(result)

