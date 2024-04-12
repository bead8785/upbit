import time
import pyupbit
import datetime

access = "access"
secret = "secret"

# Log in
upbit = pyupbit.Upbit(access, secret)
print("What's good today?")

# Print owned coins and quantities
print("My coins:")
for balance in upbit.get_balances():
    if float(balance["balance"]) > 0:
        print(f"{balance['currency']}: {balance['balance']}")

# List of coins to trade
coin_list = [
    {"ticker": "KRW-BTC", "name": "Bitcoin"},
    {"ticker": "KRW-BCH", "name": "Bitcoin Cash"},
    {"ticker": "KRW-BSV", "name": "Bitcoin SV"},
    {"ticker": "KRW-ETH", "name": "Ethereum"},
    {"ticker": "KRW-ETC", "name": "Ethereum Classic"},
    {"ticker": "KRW-BTT", "name": "BitTorrent"},
    {"ticker": "KRW-SOL", "name": "Solana"},
    {"ticker": "KRW-XLM", "name": "Stellar"},
    {"ticker": "KRW-XRP", "name": "Ripple"},
    {"ticker": "KRW-LINK", "name": "Chainlink"},
    {"ticker": "KRW-LOOM", "name": "Loom Network"},
    {"ticker": "KRW-EOS", "name": "EOS"},
    {"ticker": "KRW-ADA", "name": "Cardano"},
    {"ticker": "KRW-DOT", "name": "Polkadot"},
    {"ticker": "KRW-DOGE", "name": "Dogecoin"},
]

def get_target_price(ticker, k):
    """Get target price for buying using volatility breakout strategy"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """Get start time"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """Get 15-day moving average"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """Get balance"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """Get current price"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# Start automatic trading
while True:
    try:
        now = datetime.datetime.now()
        for balance in upbit.get_balances():
            ticker = "KRW-" + balance["currency"]
            name = next((coin["name"] for coin in coin_list if coin["ticker"] == ticker), None)
            if name is None:
                continue  # Skip coins not in coin_list

            start_time = get_start_time(ticker)
            end_time = start_time + datetime.timedelta(days=1)

            if start_time < now < end_time - datetime.timedelta(seconds=10):
                print(f"{name} ({ticker}) Buy? Sell?")
                target_price = get_target_price(ticker, 0.5)
                ma15 = get_ma15(ticker)
                current_price = get_current_price(ticker)
                if target_price < current_price and ma15 < current_price:
                    krw = get_balance("KRW")
                    if krw > 5000:
                        upbit.buy_market_order(ticker, krw*0.9995)
                        print(f"{name} ({ticker}) at {current_price} Buy")
                    else:
                        print("Show me the money!!")
                else:
                    btc = get_balance(balance["currency"])
                    if btc > 0.00008:
                        ma15 = get_ma15(ticker)
                        current_price = get_current_price(ticker)
                        if current_price > target_price and current_price > ma15:
                            upbit.sell_market_order(ticker, btc*0.9995)
                            print(f"{name} ({ticker}) at {current_price} Sell")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
