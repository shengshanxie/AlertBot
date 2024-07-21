#python 3.8 
import talib,requests,json
import pandas as pd
import numpy as np
from time import sleep
from datetime import datetime


#--------------计算指标 ------------#
def fetch_data(symbol, interval, lookback):
    base_url = 'https://api.binance.com/api/v3/klines'
    # 代理服务器的URL
    proxy = {
    "http": "http://133.18.234.13:80",
    "https": "http://160.86.242.23:8080",
}
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': lookback
    }
    response = requests.get(base_url, params=params, proxies=proxy,verify=False)
    #不使用代理服务器
    #response = requests.get(base_url, params=params, verify=False)
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
    rsi14 = talib.RSI(close, timeperiod=14)
    rsi7 = talib.RSI(close, timeperiod=7)

    # Calculate KDJ
    
    return rsi14, rsi7 #macd, signal, hist, 

tech_indicators = {
    'rsi7': np.empty(shape=(0,)),
    'rsi14': np.empty(shape=(0,)),
    #'macd': np.empty(shape=(0,)),
    #'hist': np.empty(shape=(0,)),
    #'signal': np.empty(shape=(0,)),
    #'k': np.empty(shape=(0,))
}

symbols = {
    'BTCUSDT' : tech_indicators,
    'ETHUSDT' : tech_indicators.copy()
}

interval = '1d'# 天级别
lookback = 200 # 天数必须足够多，rsi等指标计算才接近binance数据

#循环直到：成功调用接口，且 前1日已收盘（今日数据已经出现）（UTC时间）
for symbol, indicators in symbols.items():
    while True:
        try:
            current_data = fetch_data(symbol, interval, lookback)
            if len(current_data):
                print('data')
                if current_data[-1:].index[0].strftime('%Y-%m-%d')==datetime.now().strftime('%Y-%m-%d'): #前1日已收盘（今日数据已经出现）
                    print('updated')
                    calculated_date = current_data[-2:-1].index[0].strftime('%Y-%m-%d') 
                    #indicators['macd'], indicators['signal'], indicators['hist'], indicators['rsi14'], indicators['rsi7'] = calculate_indicators(current_data)
                    indicators['rsi14'], indicators['rsi7'] = calculate_indicators(current_data)
                    break
        except Exception as e:
            print(type(e).__name__, str(e))
            sleep(15)

#指标
#预警条件
rsi_upper = 70.00
rsi_lower= 30.00

#alert_indicators['']=[a,b,c]
#[a,b,c]：a表示指标值，b表示环比（如天级，表示与前一天的变化比例），c表示减去阈值的差值
alert_indicators = {
    #'rsi7': [-1,0],
    #'rsi14': [-1,0],
    #'macd': [-1,0],
    #'hist': [-1,0],
    #'signal':[-1,0],
    #'k': [-1,0],
}

alert_symbols = {
    'BTCUSDT' : alert_indicators,
    'ETHUSDT' : alert_indicators.copy()
}

for symbol, indicators in symbols.items():
    #前1天rsi7
    indicator_rsi7 = round(indicators['rsi7'][-2],2)
    #前1天rsi14
    indicator_rsi14 = round(indicators['rsi14'][-2],2)
    #前1天macd
    #indicator_macd = round(indicators['macd'][-2],2)
    #前1天k

    ##前2天
    #前2天rsi7
    indicator_rsi7_before = round(indicators['rsi7'][-3],2)
    #前2天rsi14
    indicator_rsi14_before = round(indicators['rsi14'][-3],2)
    #前2天macd
    #indicator_macd_before = round(indicators['macd'][-3],2)
    #前2天k

    #如果rsi7高于上限
    if indicator_rsi7 >= rsi_upper:
        diff_thr = round(indicator_rsi7 - rsi_upper,2)
        diff_before_rate = round( (indicator_rsi7 - indicator_rsi7_before)/indicator_rsi7_before * 100,2 )
        
        alert_symbols[symbol]['rsi7']=[indicator_rsi7, diff_before_rate, diff_thr]

    #如果rsi7低于下限
    if indicator_rsi7 <= rsi_lower:
        diff_thr = round(indicator_rsi7 - rsi_lower,2)
        diff_before_rate = round( (indicator_rsi7 - indicator_rsi7_before)/indicator_rsi7_before * 100,2  )
        
        alert_symbols[symbol]['rsi7']=[indicator_rsi7, diff_before_rate, diff_thr]

    #如果rsi14高于上限
    if indicator_rsi14 >= rsi_upper:
        diff_thr = round(indicator_rsi14 - rsi_upper,2)
        diff_before_rate = round( (indicator_rsi14 - indicator_rsi14_before)/indicator_rsi14_before * 100,2  )
        alert_symbols[symbol]['rsi14']=[indicator_rsi14, diff_before_rate, diff_thr]

    #如果rsi14低于下限
    if indicator_rsi14 <= rsi_lower:
        diff_thr = round(indicator_rsi14 - rsi_lower,2)
        diff_before_rate = round( (indicator_rsi14 - indicator_rsi14_before)/indicator_rsi14_before * 100,2  )
        alert_symbols[symbol]['rsi14']=[indicator_rsi14, diff_before_rate, diff_thr]

#是否超过阈值(1)，超过则推送
is_over_thr = 0
for sym,idc in alert_symbols.items():
    if len(idc)!= 0:
        is_over_thr=1
        break


#--------------推送通知 ------------#
#推送内容
dingding_title = "指标告警"
dingding_text = """
> 告警等级：RSI高于上限或低于下限每5个点记为1颗★\n\n
>↑、↓、- 表示环比变化

""" + "收盘日期：" + calculated_date + "\n\n"


#预警等级
#rsi：高出or低于阈值每5个点（四舍五入），记为1颗★
#示例：
# - BTCUSDT rsi7 = 71.12（+12.45%） ★
# - ETHUSDT rsi14 = 10.12（-23.23%） ★★★★
for symbol,indicators in alert_symbols.items():
    for idctr,info in indicators.items():
        #print(idctr + ' ' + str(info))

        idctr_value = info[0]
        idctr_change_before = info[1]
        idctr_thr_diff = info[2]

        #计算★数量
        alert_level = round(abs(idctr_thr_diff)/5)
        stars = ''
        for _ in range(alert_level):
            stars += '★'

        #环比描述
        idctr_change_before_desc = ''
        if idctr_change_before >0:
            idctr_change_before_desc = '(↑' + str(idctr_change_before) + '%)'
        elif idctr_change_before <0:
            idctr_change_before_desc = '(↓' + str(abs(idctr_change_before)) + '%)'
        else:
            idctr_change_before_desc = '(-)' 

        #拼接消息内容
        dingding_text += symbol + " ***" + idctr + "***=**" + str(idctr_value) + "** " + idctr_change_before_desc + " " + stars + "\n\n"


        
dingding_url = 'https://oapi.dingtalk.com/robot/send?access_token=ab74749289f41421b985edc6ef2ec3fe2046badcecd1e2bf4005d699c9a46d11'

#data_content = "2024.07.11 BTC RSI(14)="+str(rsi)+"\n"+"发送于"+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

push_data = {
    "msgtype":"markdown",
    "markdown":{
        "title":dingding_title,
        "text":dingding_text
    },
    "at":{
        "isAtAll":False
    }
}
headers = {'Content-Type':'application/json;charset=utf-8'}

#超过阈值（>0）才推送
if is_over_thr >0 :
    r=requests.post(dingding_url,headers=headers,data=json.dumps(push_data))
    print('推送结果',r.json())
