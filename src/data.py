from turtle import color
from torch import seed
import yfinance as yf
import pandas as pd
from sklearn.svm import SVC
from pyts.classification import TimeSeriesForest
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from statsmodels.tsa.arima.model import ARIMA
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


def arima_pred(df):
    split = int(0.8*len(df))
    X = [x for x in df["rsi"]]
    X_train = X[:len(df) - 10]
    X_test = X[len(df) - 10:]
    history = X_train.copy()
    predictions = []
    for t in range(len(X_test)):
        model = ARIMA(history, order=(2,1,5))
        fit = model.fit()
        output = fit.forecast()
        yhat = output[0]
        predictions.append(yhat)
        obs = X_test[t]
        history.append(yhat)
        print('predicted=%f, expected=%f' % (yhat, obs))
    plt.plot(predictions)
    plt.plot(X_test, color='red')
    plt.title('TESLA Prices Prediction')
    #plt.xlabel('Date')
    #plt.ylabel('Prices')
    #plt.xticks(np.arange(881,1259,50), df.Date[881:1259:50])
    plt.legend()
    plt.show()

