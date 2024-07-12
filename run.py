#python 3.8 
import talib,requests,json
import pandas as pd
from time import sleep
from datetime import datetime

def fetch_data(symbol, interval, lookback):
    base_url = 'https://api.binance.com/api/v3/klines'
    # 代理服务器的URL
    proxy = {
    "http": "http://133.18.234.13:80",
    "https": "http://160.86.242.23:8080",
}
    params = {
        'symbol': 'BTCUSDT',
        'interval': '1d',
        'limit': 300
    }
    #response = requests.get(base_url, params=params, proxies=proxy,verify=False)
    #不使用代理服务器
    response = requests.get(base_url, params=params, verify=False)
    data = response.json()
    df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                      'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df.set_index('open_time', inplace=True)
    df['close'] = df['close'].astype(float)
    return df

def calculate_indicators(data):
    close = data['close'].values

    # Calculate MACD
    #macd, signal, hist = talib.MACD(
    #    close, fastperiod=12, slowperiod=26, signalperiod=9)

    # Calculate RSI
    rsi = talib.RSI(close, timeperiod=14)

    #return macd, signal, hist, rsi
    return rsi

symbol = 'BTCUSDT'
interval = '1d'
lookback = 300
while True:
    try:
      data = fetch_data(symbol, interval, lookback)
      if len(data):
          rsi = calculate_indicators(data)[-2]
          break
    except Exception as e:
        sleep(20)

dingding_url = 'https://oapi.dingtalk.com/robot/send?access_token=ab74749289f41421b985edc6ef2ec3fe2046badcecd1e2bf4005d699c9a46d11'

data_content = "2024.07.11 BTC RSI(14)="+str(rsi)+"\n"+"发送于"+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

push_data = {
    "msgtype":"text",
    "text":{
        "content":data_content
    },
    "at":{
        "isAtAll":False
    }
}
headers = {'Content-Type':'application/json;charset=utf-8'}

r=requests.post(dingding_url,headers=headers,data=json.dumps(push_data))
