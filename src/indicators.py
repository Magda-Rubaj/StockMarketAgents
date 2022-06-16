import pandas as pd
import pandas_ta as ta
import yfinance as yf


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
    df2 = macd[33:].filter(['Date'], axis=1)
    df2 = df2.assign(macd='NAN')
    sliced = macd[33:]
    df2 = sliced.filter(['Date'], axis=1)
    is_above = -1
    is_above = 1 if sliced['MACD_12_26_9'][0] > sliced['MACDs_12_26_9'][0] else 0
    for index, value in sliced.iterrows():
        if value['MACD_12_26_9'] > value['MACDs_12_26_9'] and not is_above:
            buysell.append('buy')
            is_above = 1
        elif value['MACD_12_26_9'] < value['MACDs_12_26_9'] and is_above:
            buysell.append('sell')
            is_above = 0
        else:
            buysell.append(None)
    df2['macd'] = buysell
    return df2

def make_decisions_table(df):
    macd  = calculate_macd(df)
    table = macd_decisions(macd)
    table['price'] = df['Close']
    return table


