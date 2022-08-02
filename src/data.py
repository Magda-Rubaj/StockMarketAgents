import yfinance as yf
import pandas as pd


def calculate_df(symbol):
    df = pd.DataFrame()
    df = yf.Ticker(symbol)
    df = df.history(start='2019-01-01', end='2022-07-22', interval="5d")
    df = df.reset_index()
    return df


def transform_df(df, n):
    df2 = pd.DataFrame()
    for i in range(n + 1, len(df)):
        df2.loc[i, "date"] = df.loc[i, "Date"]
        df2.loc[i, "momentum"] = df.iloc[i - 1]["Close"] - df.iloc[i - (n + 1)]["Close"]
        df2.loc[i, "volatility"] = df.iloc[i - (n + 1): i - 1]["Close"].std()
        df2.loc[i, "max"] = df.iloc[i - (n + 1): i - 1]["High"].max()
        df2.loc[i, "min"] = df.iloc[i - (n + 1): i - 1]["Low"].min()
        df2.loc[i, "last"] = df.iloc[i - 1]["Close"]
        df2.loc[i, "up"] = 1 if df.iloc[i - 1]["Close"] < df.iloc[i]["Close"] else 0
    df2 = df2.reset_index(drop=True)
    return df2


