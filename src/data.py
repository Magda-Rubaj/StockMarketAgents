from typing import List
import yfinance as yf
import pandas as pd
from dateutil.parser import parse
from sklearn.impute import SimpleImputer
from indicators import calculate_rsi, calculate_ema


def include_fundamentals(earnings: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    for i in range(len(earnings)):
        earnings.loc[i, "Earnings Date"] = parse(earnings.iloc[i]["Earnings Date"][:12])
    earnings = earnings.sort_values(by=["Earnings Date"])
    for i in range(len(df)):
        for j in range(len(earnings) - 1):
            if (
                earnings.iloc[j]["Earnings Date"]
                <= df.iloc[i]["Date"]
                < earnings.iloc[j + 1]["Earnings Date"]
            ):
                df.loc[i, "eps"] = earnings.iloc[j]["Reported EPS"]
                continue
    return df


def get_initial_df(symbol: str, start: str, end: str) -> pd.DataFrame:
    df = pd.DataFrame()
    df = yf.Ticker(symbol)
    earnings = df.earnings_history
    df = df.history(start=start, end=end, interval="1wk")
    df = df.reset_index(drop=False)
    if earnings is not None:
        df = include_fundamentals(earnings, df)
    return df


def get_ml_df(df: pd.DataFrame, n: int) -> pd.DataFrame:
    df["rsi"] = calculate_rsi(df, 14)
    df["ema50"] = calculate_ema(df, 50)
    df["ema10"] = calculate_ema(df, 20)
    df2 = pd.DataFrame()
    for i in range(n + 1, len(df)):
        df2.loc[i, "momentum"] = df.iloc[i - 1]["Close"] - df.iloc[i - (n + 1)]["Close"]
        df2.loc[i, "rsi"] = df.iloc[i]["rsi"]
        df2.loc[i, "ema50"] = df.iloc[i]["ema50"]
        df2.loc[i, "eps"] = df.iloc[i]["eps"]
        df2.loc[i, "up"] = 1 if df.iloc[i - 1]["Close"] < df.iloc[i]["Close"] else 0
    df2 = df2.reset_index()
    imp = SimpleImputer()
    idf = pd.DataFrame(imp.fit_transform(df2))
    idf.columns = df2.columns
    idf.index = df2.index
    return idf


def get_ema_data(df: pd.DataFrame, minimal_index: int) -> List[dict]:
    df["ema50"] = calculate_ema(df, 50)
    df["ema10"] = calculate_ema(df, 10)
    df = df[minimal_index:]
    df = df.reset_index(drop=True)
    prices = df["Close"]
    loop_data = [
        {"input_data": df.iloc[i], "price": prices[i]} for i in range(len(prices))
    ]
    return loop_data


def get_ml_data(df: pd.DataFrame, split: int, prices: List[float]):
    y = df["up"]
    X = df.loc[:, df.columns != "up"]
    train_data = {"X_train": X[:split], "y_train": y[:split], "prices": prices[split:]}
    loop_data = [
        {"input_data": X.iloc[i], "price": prices[i]}
        for i in range(len(prices[split:]))
    ]
    return train_data, loop_data


def get_arima_data(df: pd.DataFrame, minimal_index: int):
    prices = df["Close"]
    train_data = {"prices": prices[:minimal_index]}
    loop_data = [{"price": prices[i]} for i in range(minimal_index, len(prices))]
    return train_data, loop_data


def get_data(initial_df: pd.DataFrame, data_type: str):
    ml_df = get_ml_df(initial_df, 50)
    split = int(0.7 * len(ml_df))
    diff = len(initial_df) - len(ml_df)  # we want to have test data for all strategies having same length
    minimal_index = 50 if diff < 50 else diff # since we calculate ema50
    cropped_df = initial_df[minimal_index:]
    cropped_df = cropped_df.reset_index(drop=True)
    prices = cropped_df["Close"]
    mapping = {
        "arima": get_arima_data(cropped_df, split),
        "ml": get_ml_data(ml_df, split, prices),
        "ema": get_ema_data(initial_df, minimal_index + split),
    }
    return mapping.get(data_type)
