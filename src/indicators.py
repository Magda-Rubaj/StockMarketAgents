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


class RSIEMACrossoverStrategy:
    def __init__(self):
        #self.rsi_crossed = False
        self.ema_crossed = False
        self.is_above = -1
    
    def first_value(self, value):
        self.is_above = 1 if value["price"] > value["ema"] else 0

    def buy_condition(self, price, ema):
        if price > ema and not self.is_above:
            self.ema_crossed = True
            self.is_above = 1
            return "buy"
        return False

    def sell_condition(self, value):
        if value["price"] < value["ema"] and self.is_above:
            self.ema_crossed = True
            self.is_above = 0
            return "sell"
        return False

    def execute(self, value):
        return self.buy_condition(value) or self.sell_condition(value["ema"])


def make_decisions_table(df):
    macd = calculate_macd(df)
    df['ema50'] = calculate_ema(df, 50)
    df['ema10'] = calculate_ema(df, 10)
    df['price'] = df['Close']
    df = df[50:]
    return df
