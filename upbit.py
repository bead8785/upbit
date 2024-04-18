import time
import pyupbit
import datetime
from slack_sdk import WebClient
import slack_sdk
import os

# Slack API 토큰
slack_token = "slack_token"
slack_client = WebClient(token=slack_token)

access = "access"
secret = "secret"

# Slack 클라이언트 초기화
slack_client = slack_sdk.WebClient(token=slack_token)

def send_slack_message(message):
    try:
        # Slack으로 메시지 전송
        response = slack_client.chat_postMessage(channel='#coin', text=message)
        if response["ok"]:
            print("Slack 메시지가 성공적으로 전송되었습니다.")
        else:
            print("Slack 메시지 전송에 실패하였습니다.")
    except Exception as e:
        print(f"Slack 메시지 전송 중 오류 발생: {e}")

coin_list = [
    {"ticker": "BTC", "name": "비트코인"},
    {"ticker": "BSV", "name": "비트코인 에스브이"},
    {"ticker": "ETH", "name": "이더리움"},
    {"ticker": "ETC", "name": "이더리움클래식"},
    {"ticker": "BTT", "name": "비트토렌트"},
    {"ticker": "SOL", "name": "솔라나"},
    {"ticker": "XLM", "name": "스텔라루멘"},
    {"ticker": "XRP", "name": "리플"},
    {"ticker": "LINK", "name": "체인링크"},
    {"ticker": "LOOM", "name": "룸네트워크"},
    {"ticker": "EOS", "name": "이오스"},
    {"ticker": "ADA", "name": "에이다"},
    {"ticker": "DOT", "name": "폴카닷"},
    {"ticker": "DOGE", "name": "도지코인"},
    {"ticker": "SHIB", "name": "시바이누"},
]

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
                return float(b['balance']), float(b['avg_buy_price'])
            else:
                return 0, 0
    return 0, 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 매수 기록을 저장할 리스트
buy_history = []

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        holding_coins = []
        for coin in coin_list:
            ticker = f"KRW-{coin['ticker']}"
            balance, avg_buy_price = get_balance(coin['ticker'])
            if balance > 0:
                holding_coins.append(coin)
                start_time = get_start_time(ticker)
                end_time = start_time + datetime.timedelta(days=1)

                if start_time < now < end_time - datetime.timedelta(seconds=10):
                    target_price = get_target_price(ticker, 0.5)
                    ma15 = get_ma15(ticker)
                    current_price = get_current_price(ticker)
                    print(f"{coin['name']} 보유량: {balance}, 평균매수가: {avg_buy_price}, 현재가: {current_price}, 목표가: {target_price}, 15일 이동평균가: {ma15}")
                    message = f"{coin['name']} 보유량: {balance}, 평균매수가: {avg_buy_price}, 현재가: {current_price}, 목표가: {target_price}, 15일 이동평균가: {ma15}"
                    send_slack_message(message)
                    if target_price < current_price and ma15 < current_price:
                        krw = get_balance("KRW")
                        if krw > 5000:
                            buy_amount = krw * 0.9995
                            upbit.buy_market_order(ticker, buy_amount)
                            # 매수한 내역 저장
                            buy_history.append({"coin": coin['name'], "amount": buy_amount})
                            print(f"매수: {coin['name']} {buy_amount} 원")
                else:
                    if ma15 > current_price:
                        loss_rate = (current_price - avg_buy_price) / avg_buy_price
                        if loss_rate < -0.03:
                            sell_amount = balance * 0.9995
                            upbit.sell_market_order(ticker, sell_amount)
                            print(f"매도: {coin['name']} 매도가: {current_price}, 손실률: {loss_rate}")
                            message = f"매도: {coin['name']} 매도가: {current_price}, 손실률: {loss_rate}"
                            send_slack_message(message)
        if len(holding_coins) == 0:
            for coin in coin_list:
                ticker = f"KRW-{coin['ticker']}"
                start_time = get_start_time(ticker)
                end_time = start_time + datetime.timedelta(days=1)
                if start_time < now < end_time - datetime.timedelta(seconds=10):
                    target_price = get_target_price(ticker, 0.5)
                    ma15 = get_ma15(ticker)
                    current_price = get_current_price(ticker)
                    print(f"{coin['name']} 현재가: {current_price}, 목표가: {target_price}, 15일 이동평균가: {ma15}")
                    message = f"{coin['name']} 현재가: {current_price}, 목표가: {target_price}, 15일 이동평균가: {ma15}"
                    send_slack_message(message)
                    if target_price < current_price and ma15 < current_price:
                        krw = get_balance("KRW")
                        if krw > 5000:
                            upbit.buy_market_order(ticker, krw*0.9995)
                            print(f"매수: {coin['name']} 매수가: {current_price}, 목표가: {target_price}, 평균가: {avg_buy_price}")
                            message = f"매수: {coin['name']} 매수가: {current_price}, 목표가: {target_price}, 평균가: {avg_buy_price}"
                            send_slack_message(message)
                            
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
