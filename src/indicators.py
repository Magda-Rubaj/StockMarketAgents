import pandas as pd
import pandas_ta as ta
import yfinance as yf


def calculate_adx(df):
    return ta.adx(high=df['High'], low=df['Low'], close=df['Close'])


def calculate_macd(df):
    return ta.macd(close=df['Close'])


def calculate_stochastic(df):
    return ta.stoch(high=df['High'], low=df['Low'], close=df['Close'])


def determine_trend(df):
    adx = calculate_adx(df)
    adx_trend = []
    for index, value in adx[33:].iterrows():
        if value['ADX_14'] < 25:
            adx_trend.append("no trend")
        elif value['ADX_14'] >= 40:
            adx_trend.append("strong trend")
        else:
            adx_trend.append("regular trend")
    return adx_trend


def determine_stochastic(df):
    stochastic = calculate_stochastic(df)
    values = []
    for index, value in stochastic[20:].iterrows():
        if value['STOCHk_14_3_3'] < 20:
            values.append("oversold")
        elif value['STOCHk_14_3_3'] > 80:
            values.append("overbought")
        else:
            values.append(None)
    print(stochastic)
    return values


def macd_decisions(macd):
    buysell = []
    sliced = macd[33:]
    df2 = sliced.filter(['Date'], axis=1)
    df2 = df2.assign(macd='NAN')
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
    macd = calculate_macd(df)
    adx = determine_trend(df)
    stochastic = determine_stochastic(df)
    table = macd_decisions(macd)
    table['trend'] = adx
    table['stochastic'] = stochastic
    table['price'] = df['Close']
    print(table)

    return table
