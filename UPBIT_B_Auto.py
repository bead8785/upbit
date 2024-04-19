import time
import pyupbit
import datetime
import numpy as np

# access key와 secret key를 파일에서 읽어오는 함수
def read_keys_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        access_key = lines[1].strip().split('= ')[1].strip()  # 엑세스 키 읽어오기
        secret_key = lines[2].strip().split('= ')[1].strip()  # 시크릿 키 읽어오기
        coin_dict = {}
        for line in lines[5:]:
            if '=' in line:  # 코인 정보가 있는 라인인지 확인
                parts = line.strip().split('=')  # 코인 코드와 한글명 분리
                coin_code = parts[0].strip()
                coin_name = '='.join(parts[1:]).strip()  # 한글명에 '=' 기호 포함할 수 있으므로 나머지 부분을 합침
                coin_dict[coin_code] = coin_name  # 딕셔너리에 저장
        coin_list = list(coin_dict.keys())  # 코인 코드 리스트 생성
    return access_key, secret_key, coin_dict, coin_list

# access key와 secret key를 파일에서 읽어옴
access, secret, coin_dict, coin_list = read_keys_from_file("UPBIT_B_Auto.txt")
print(f"거래되는 코인{coin_list}")

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("자동매매시작")

# 가격 형식화 함수
def format_price(amount):
    """금액 포맷팅"""
    if amount >= 100:
        return f"{amount:,.1f}"
    else:
        return f"{amount:.6f}"
    
# 보유한 코인과 수량 출력
print("내 보유코인:")
for balance in upbit.get_balances():
    currency = balance["currency"]
    balance_amount = float(balance["balance"])
    if balance_amount > 0 and (currency == 'KRW' or currency in coin_list):
        print(f"{currency}: {format_price(balance_amount)}")

# RSI 계산 함수
def calculate_rsi(ticker, period=14):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=period+1)
    df['close_delta'] = df['close'].diff()
    df['gain'] = np.where(df['close_delta'] > 0, df['close_delta'], 0)
    df['loss'] = np.where(df['close_delta'] < 0, abs(df['close_delta']), 0)
    avg_gain = df['gain'].rolling(window=period).mean()
    avg_loss = df['loss'].rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# 이동 평균 거래량 계산 함수
def calculate_ma_volume(ticker, days):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=days)
    ma_volume = df['volume'].rolling(window=days).mean().iloc[-1]
    return ma_volume

# 볼린저 밴드 상태 확인 함수
def check_bollinger_band(ticker, std_dev=2):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
    middle_band = df['close'].rolling(window=20).mean().iloc[-1]
    std = df['close'].rolling(window=20).std().iloc[-1]
    upper_band = middle_band + std_dev * std
    lower_band = middle_band - std_dev * std
    current_price = pyupbit.get_current_price(ticker)
    if current_price > upper_band:
        return 'high'
    elif current_price < lower_band:
        return 'low'
    else:
        return 'normal'

def get_balance_info(ticker):
    """보유한 코인의 정보 조회"""
    balances = upbit.get_balances()
    for balance in balances:
        if balance['currency'] == ticker:
            coin_balance = float(balance['balance'])
            avg_buy_price = float(balance['avg_buy_price'])
            current_price = pyupbit.get_current_price(f"KRW-{ticker}")
            return coin_balance, avg_buy_price, current_price
    return 0, 0, 0

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        
        # 보유 중인 코인 확인
        holding_coins = [balance["currency"] for balance in upbit.get_balances() if float(balance["balance"]) > 0]

        # COIN_LIST에 포함된 각 코인에 대해 반복
        for coin_code in coin_list:
            coin_name = coin_dict.get(coin_code)  # 코인 코드에 해당하는 한글명 가져오기
            target_ticker = f"KRW-{coin_code}"
            
            coin_balance, avg_buy_price, current_price = get_balance_info(coin_code)
            
            # 보유 중인 코인인 경우 매도 조건 검색
            if coin_balance > 0:
                rsi = calculate_rsi(target_ticker)
                bollinger_state = check_bollinger_band(target_ticker)
                print(f"{coin_name} - RSI : {'OK' if rsi >= 70 else 'NO'}, 볼린저 밴드 상태: {'OK' if bollinger_state == 'low' else bollinger_state}")
                if rsi >= 70 and bollinger_state == 'low':
                    upbit.sell_market_order(target_ticker, coin_balance * 0.9995)
                    print(f"{coin_name} - RSI가 70 이상이고 볼린저 밴드가 하단에 있으므로 코인을 매도하였습니다.")
            
            # 보유 중이지 않은 코인인 경우 매수 조건 검색
            elif not holding_coins:
                rsi = calculate_rsi(target_ticker)
                bollinger_state = check_bollinger_band(target_ticker)
                ma_5_volume = calculate_ma_volume(target_ticker, 5)
                ma_10_volume = calculate_ma_volume(target_ticker, 10)
                ma_20_volume = calculate_ma_volume(target_ticker, 20)
                print(f"{coin_name} - 현재 가격: {format_price(current_price)}, RSI : {'OK' if rsi <= 30 else 'NO'}, 볼린저 밴드 상태: {'OK' if bollinger_state == 'high' else bollinger_state}, 거래량: {'OK' if ma_5_volume > ma_10_volume and ma_5_volume > ma_20_volume else 'NO'}")
                
                if rsi <= 30 and (bollinger_state == 'high' or ma_5_volume > ma_10_volume and ma_5_volume > ma_20_volume):
                    krw_balance = upbit.get_balance("KRW")
                    if krw_balance > 5000:
                        upbit.buy_market_order(target_ticker, krw_balance * 0.9995)
                        print(f"{coin_name} - RSI가 30 이하이고 볼린저 밴드가 상단에 있거나 5일 이동 평균 거래량이 10일 및 20일 이동 평균 거래량보다 크므로 코인을 매수하였습니다.")

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
