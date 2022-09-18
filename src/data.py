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
    return df2


def get_ema_data(df, minimal_index):
    df["ema50"] = calculate_ema(df, 50)
    df["ema10"] = calculate_ema(df, 10)
    df = df[50:]
    df = df[minimal_index:]
    df = df.reset_index(drop=True)
    prices = df["Close"]
    loop_data = [{
        "input_data": df.iloc[i],
        "price": prices[i]
    } for i in range(len(prices))]
    return loop_data


def get_ml_data(df, split, prices):
    y = df["up"]
    X = df.loc[:, df.columns != 'up']
    train_data = {
        "X_train": X[:split],
        "y_train": y[:split],
        "prices": prices[split:]
    }
    loop_data = [{
        "input_data": X.iloc[i],
        "price": prices[i]
    } for i in range(len(prices[split:]))]
    return train_data, loop_data


def get_arima_data(df, minimal_index):
    prices = df["Close"]
    train_data = {
        "prices": prices[:minimal_index]
    }
    loop_data = [{
        "price": prices[i]
    } for i in range(minimal_index, len(prices))]
    return train_data, loop_data


def get_data(initial_df, data_type):
    ml_df = get_ml_df(initial_df, 20)
    split = int(0.8*len(ml_df))
    minimal_index = len(initial_df) - len(ml_df)
    cropped_df = initial_df[minimal_index:]
    prices = initial_df[minimal_index:]["Close"]
    mapping = {
        "arima": get_arima_data(cropped_df, split),
        "ml": get_ml_data(ml_df, split, prices),
        "ema": get_ema_data(initial_df, minimal_index + split)
    }
    return mapping.get(data_type)



