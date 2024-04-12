import time
import pyupbit
import datetime

access = "access"
secret = "secret"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("오늘은 뭐가 좋을까?")

# 보유한 코인과 수량 출력
print("내 보유코인:")
for balance in upbit.get_balances():
    if float(balance["balance"]) > 0:
        print(f"{balance['currency']}: {balance['balance']}")

# 매도할 코인 리스트
coin_list = [
    {"ticker": "KRW-BTC", "name": "비트코인"},
    {"ticker": "KRW-BCH", "name": "비트코인 캐시"},
    {"ticker": "KRW-BSV", "name": "비트코인 에스브이"},
    {"ticker": "KRW-ETH", "name": "이더리움"},
    {"ticker": "KRW-ETC", "name": "이더리움클래식"},
    {"ticker": "KRW-BTT", "name": "비트토렌트"},
    {"ticker": "KRW-SOL", "name": "솔라나"},
    {"ticker": "KRW-XLM", "name": "스텔라루멘"},
    {"ticker": "KRW-XRP", "name": "리플"},
    {"ticker": "KRW-LINK", "name": "체인링크"},
    {"ticker": "KRW-LOOM", "name": "룸네트워크"},
    {"ticker": "KRW-EOS", "name": "이오스"},
    {"ticker": "KRW-ADA", "name": "에이다"},
    {"ticker": "KRW-DOT", "name": "폴카닷"},
    {"ticker": "KRW-DOGE", "name": "도지코인"},
]

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        for balance in upbit.get_balances():
            ticker = "KRW-" + balance["currency"]
            name = next((coin["name"] for coin in coin_list if coin["ticker"] == ticker), None)
            if name is None:
                continue  # coin_list에 없는 코인은 건너뜁니다.

            start_time = get_start_time(ticker)
            end_time = start_time + datetime.timedelta(days=1)

            if start_time < now < end_time - datetime.timedelta(seconds=10):
                print(f"{name} ({ticker})고민 중...")
                target_price = get_target_price(ticker, 0.5)
                ma15 = get_ma15(ticker)
                current_price = get_current_price(ticker)
                if target_price < current_price and ma15 < current_price:
                    krw = get_balance("KRW")
                    if krw > 5000:
                        upbit.buy_market_order(ticker, krw*0.9995)
                        print(f"{name} ({ticker}) at {current_price} 매수")
                    else:
                        print("사고픈데 돈이없다..")
            else:
                btc = get_balance(balance["currency"])
                if btc > 0.00008:
                    ma15 = get_ma15(ticker)
                    current_price = get_current_price(ticker)
                    if current_price > target_price and current_price > ma15:
                        upbit.sell_market_order(ticker, btc*0.9995)
                        print(f"{name} ({ticker}) at {current_price} 매도")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
