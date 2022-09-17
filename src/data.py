import yfinance as yf
import pandas as pd
from sklearn.svm import SVC
from pyts.classification import TimeSeriesForest
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
#from statsmodels.tsa.arima.model import ARIMA
from indicators import calculate_rsi, calculate_ema


def get_initial_df(symbol, start, end):
    df = pd.DataFrame()
    df = yf.Ticker(symbol)
    df = df.history(start=start, end=end, interval="1d")
    return df


def get_ml_df(df, n):
    df["rsi"] = calculate_rsi(df, 14)
    df["ema50"] = calculate_ema(df, 50)
    df["ema10"] = calculate_ema(df, 20)
    df2 = pd.DataFrame()
    for i in range(n + 1, len(df)):
        df2.loc[i, "momentum"] = df.iloc[i - 1]["Close"] - df.iloc[i - (n + 1)]["Close"]
        df2.loc[i, "rsi"] = df.iloc[i]["rsi"]
        df2.loc[i, "ema50"] = df.iloc[i]["ema50"]
        df2.loc[i, "up"] = 1 if df.iloc[i - 1]["Close"] < df.iloc[i]["Close"] else 0
    df2 = df2.reset_index(drop=True)
    df2 = df2[30:]
    y = df2["up"]
    X = df2.loc[:, df2.columns != 'up']
    return X, y, df["Close"][n + 31:]


def get_ema_df(df):
    df["ema50"] = calculate_ema(df, 50)
    df["ema10"] = calculate_ema(df, 10)
    df = df[50:]
    prices = df["Close"]
    df = df.reset_index(drop=True)
    loop_data = [{
        "input_data": df.iloc[i],
        "price": prices[i]
    } for i in range(len(prices))]
    return loop_data



