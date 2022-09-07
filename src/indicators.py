import pandas as pd
import pandas_ta as ta
import yfinance as yf


def calculate_adx(df):
    return ta.adx(high=df['High'], low=df['Low'], close=df['Close'])

def calculate_ema(df, period):
    return ta.ema(df["Close"], length=period)

def calculate_rsi(df, period):
    return ta.rsi(close=df['Close'], length=period)

def calculate_macd(df):
    return ta.macd(close=df['Close'])

def calculate_stochastic(df):
    return ta.stoch(high=df['High'], low=df['Low'], close=df['Close'])
    

