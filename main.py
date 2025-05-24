import os
import requests
import logging
from datetime import datetime, timedelta
from telegram import Bot

# Логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# Binance API
BINANCE_API_URL = "https://api.binance.com"

def get_binance_symbols():
    url = f"{BINANCE_API_URL}/api/v3/exchangeInfo"
    response = requests.get(url)
    symbols = {
        s["symbol"]
        for s in response.json()["symbols"]
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"
    }
    return symbols

def get_binance_kline(symbol: str, interval: str = "1m", limit: int = 30):
    url = f"{BINANCE_API_URL}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def analyze_symbol(symbol):
    try:
        klines = get_binance_kline(symbol)
        if len(klines) < 30:
            return None

        first = klines[0]
        last = klines[-1]

        open_price = float(first[1])
        close_price = float(last[4])
        price_change = (close_price - open_price) / open_price * 100

        volume_start = sum(float(k[5]) for k in klines[:15])
        volume_end = sum(float(k[5]) for k in klines[15:])
        volume_change = (volume_end - volume_start) / volume_start * 100 if volume_start else 0

        if price_change > 3 and volume_change > 100:
            return {
                "symbol": symbol,
                "price_change": round(price_change, 2),
                "volume_change": round(volume_change, 2)
            }

    except Exception as e:
        logging.warning(f"Ошибка при анализе {symbol}: {e}")
    return None

def main():
    logging.info("🚀 Старт анализа Binance...")
    symbols = get_binance_symbols()
    logging.info(f"📊 Найдено {len(symbols)} символов")

    pump_candidates = []

    for symbol in symbols:
        result = analyze_symbol(symbol)
        if result:
            pump_candidates.append(result)

    if pump_candidates:
        message = "🔥 Потенциальные пампы на Binance:\n"
        for pump in pump_candidates:
            message += f"\n🟢 {pump['symbol']}: +{pump['price_change']}% цены, +{pump['volume_change']}% объёма"
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    else:
        logging.info("📉 Пампов не обнаружено.")
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Сегодня пампов не обнаружено.")

if __name__ == "__main__":
    main()
