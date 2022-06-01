import pandas as pd
import pandas_ta as ta
import yfinance as yf


df = pd.DataFrame() 
df = yf.Ticker("^gspc")
df = df.history(start='2021-01-03', end='2021-03-10')

def calculate_adx(df):
    return ta.adx(high=df['High'],low=df['Low'],close=df['Close'])


def calculate_macd(df):
    return ta.macd(close=df['Close'])


def determine_trend(df):
    adx = calculate_adx(df)
    if adx['ADX_14'] < 25:
        trend = "no trend"
    elif adx['ADX_14'] >= 40:
        trend = "strong trend"
    else:
        trend = "regular trend"
    return trend


def macd_decisions(macd):
    buysell = []
    is_above = -1
    is_above = 1 if macd['MACD_12_26_9'][0] > macd['MACDs_12_26_9'][0] else 0
    for i in range(1, len(macd)):
        if macd['MACD_12_26_9'][i] > macd['MACDs_12_26_9'][i] and not is_above:
            buysell.append('buy')
            is_above = 1
        elif macd['MACD_12_26_9'][i] < macd['MACDs_12_26_9'][i] and is_above:
            buysell.append('sell')
            is_above = 0
        else:
            buysell.append(None)
    return buysell

print(calculate_macd(df))

