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


