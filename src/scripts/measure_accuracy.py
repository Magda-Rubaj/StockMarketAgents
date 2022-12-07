import pandas as pd
from sklearn.metrics import accuracy_score
from strategies import SVCStrategy
from sklearn.svm import SVC
from pyts.classification import TimeSeriesForest
from sklearn.impute import SimpleImputer
from statsmodels.tsa.stattools import adfuller
from sklearn import preprocessing
from data import get_svc_df
import os


def test_stationarity(vals):
    test_results = adfuller(vals)

    print(f"ADF test statistic: {test_results[0]}")
    print(f"p-value: {test_results[1]}")
    print("Critical thresholds:")

    for key, value in test_results[4].items():
        print(f"\t{key}: {value}")

        
def measure_accuracy(interval):
    files = [f for f in os.listdir('./csv')]
    files = [file for file in files if interval in file]
    sum_acc = 0
    for file in files:
        df = pd.read_csv(f"csv/{file}")
        df["Close"] = df["Close"].fillna(method="ffill")
        ml_df = get_svc_df(df, 50)
        y = ml_df["up"]
        #test_stationarity(df["Close"])
        X = ml_df.drop('up', axis=1)
        split = int(0.7 * len(ml_df))
        train_data = {"X_train": X[:split], "y_train": y[:split]}
        lab = preprocessing.LabelEncoder()
        y_transformed = lab.fit_transform(y)
        test_X, test_y = X[split:], y_transformed[split:]
        model = SVC(random_state=123).fit(
            X[:split], y_transformed[:split]
        )
        predictions = model.predict(test_X)
        sum_acc += accuracy_score(test_y, predictions, normalize=True)
    print(sum_acc / len(files))
        



if __name__ == "__main__":
    measure_accuracy("1wk")
    measure_accuracy("1d")
    measure_accuracy("5d")