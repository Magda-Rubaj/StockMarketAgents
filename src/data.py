import yfinance as yf
import pandas as pd
from sklearn.svm import SVC
from pyts.classification import TimeSeriesForest
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


def calculate_df(symbol):
    df = pd.DataFrame()
    df = yf.Ticker(symbol)
    df = df.history(start='2010-01-01', end='2022-07-30', interval="1mo")
    df = df.reset_index()
    return df


def transform_df(df, n):
    df2 = pd.DataFrame()
    for i in range(n + 1, len(df)):
        #df2.loc[i, "date"] = df.loc[i, "Date"]
        df2.loc[i, "momentum"] = df.iloc[i - 1]["Close"] - df.iloc[i - (n + 1)]["Close"]
        df2.loc[i, "volatility"] = df.iloc[i - (n + 1): i - 1]["Close"].std()
        #df2.loc[i, "max"] = df.iloc[i - (n + 1): i - 1]["High"].max()
        #df2.loc[i, "min"] = df.iloc[i - (n + 1): i - 1]["Low"].min()
        df2.loc[i, "last"] = df.iloc[i - 1]["Close"]
        df2.loc[i, "up"] = 1 if df.iloc[i - 1]["Close"] < df.iloc[i]["Close"] else 0
    df2 = df2.reset_index(drop=True)
    return df2


def train_svc(df):
    split = int(0.8*len(df))
    y = df["up"]
    X = df.loc[:, df.columns != 'up']
    X_train = X[:split]
    y_train = y[:split]
    X_test = X[split:]
    y_test = y[split:]
    model = TimeSeriesForest().fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(y_pred)
    print(list(y_test))
    print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
    
df = transform_df(calculate_df("fb"), 10)
print(df)
train_svc(df)