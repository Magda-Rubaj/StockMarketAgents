import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, mean_absolute_error
from matplotlib import pyplot
from sklearn.svm import SVC
from statsmodels.tsa.arima.model import ARIMA
from sklearn.impute import SimpleImputer
from statsmodels.tsa.stattools import adfuller
from sklearn import preprocessing
from logger import logger
from math import sqrt
from data import get_svc_df, get_df_from_api
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
    sum_f1 = 0
    for file in files:
        df = pd.read_csv(f"csv/{file}")
        df["Close"] = df["Close"].fillna(method="ffill")
        ml_df = get_svc_df(df)
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
        sum_f1 += f1_score(test_y, predictions)
        sum_acc += accuracy_score(test_y, predictions, normalize=True)
    print(interval)
    print("accuracy:", (sum_acc / len(files)))
    print("f1:", (sum_f1 / len(files)))


def measure_arima_accuracy(interval):
    files = [f for f in os.listdir('./csv')]
    files = [file for file in files if interval in file]
    sum_acc = 0
    for file in files:
        df = pd.read_csv(f"csv/{file}")
        df["Close"] = df["Close"].fillna(method="ffill")
        y = df["Close"]
        split = int(0.7 * len(df))
        test = list(y[split:])
        history = list(y[:split])
        predictions = []
        for t in range(len(test)):
            model = ARIMA(history, order=(0,1,2))
            model_fit = model.fit()
            output = model_fit.forecast()
            yhat = output[0]
            predictions.append(yhat)
            obs = test[t]
            history.append(obs)
        sum_acc += mean_absolute_error(test, predictions)
        # if interval == "1d" and "tsla" in file:
        #     pyplot.plot(test, label="Original data")
        #     pyplot.plot(predictions, color='red', label="ARIMA predictions")
        #     pyplot.ylabel('Price')
        #     pyplot.xlabel('Days')
        #     pyplot.legend()
        #     pyplot.show()
        #     pyplot.plot(test[:50], label="Original data")
        #     pyplot.plot(predictions[:50], color='red', label="ARIMA predictions")
        #     pyplot.ylabel('Price')
        #     pyplot.xlabel('Days')
        #     pyplot.legend()
        #     pyplot.show()
    logger.info(f"{interval} mae:, {(sum_acc / len(files))}")


def showsp500():
    initial_df = get_df_from_api("^gspc", "2013-01-01", "2018-01-01", "5d")
    print(initial_df)
    initial_df["Date"] = initial_df["Date"].map(lambda t: t.strftime('%Y-%m-%d'))
    default_x_ticks = range(len(initial_df["Date"]))
    pyplot.xticks(default_x_ticks, initial_df["Date"], rotation = 40)
    ax = pyplot.gca()
    ax.set_xticks(ax.get_xticks()[::50])
    pyplot.plot(initial_df["Close"], label="S&P500 price")
    pyplot.ylabel('Price')
    pyplot.xlabel('Days')
    pyplot.legend()
    pyplot.show()

        



if __name__ == "__main__":
    showsp500()
    # measure_accuracy("1wk")
    # measure_accuracy("1d")
    # measure_accuracy("5d")
    # measure_accuracy("1h")
    # measure_accuracy("15m")
    # measure_accuracy("5m")
    # measure_arima_accuracy("1wk")
    # measure_arima_accuracy("1d")
    # measure_arima_accuracy("5d")
    # measure_arima_accuracy("1h")
    # measure_arima_accuracy("15m")
    # measure_arima_accuracy("5m")