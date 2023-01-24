from typing import Literal
from pyts.classification import TimeSeriesForest
from sklearn.svm import SVC
from statsmodels.tsa.arima.model import ARIMA
from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):
    @abstractmethod
    def execute(self, input_data: dict, stock: str):
        raise NotImplementedError


class EMACrossoverStrategy(Strategy):
    def __init__(self, data: dict):
        self.ema_crossed = False
        self.is_above = {}
        for key, val in data.items():
            self.is_above[key] = (
                1
                if val[0]["input_data"]["ema10"]
                > val[0]["input_data"]["ema50"]
                else 0
            )

    def buy_condition(self, value, stock: str) -> Literal["str", None]:
        value = value["input_data"]
        if value["ema10"] > value["ema50"] and not self.is_above[stock]:
            self.ema_crossed = True
            self.is_above[stock] = 1
            return "buy"

    def sell_condition(self, value, stock: str) -> Literal["str", None]:
        value = value["input_data"]
        if value["ema10"] < value["ema50"] and self.is_above[stock]:
            self.ema_crossed = True
            self.is_above[stock] = 0
            return "sell"

    def execute(self, input_data: dict, stock: str) -> Literal["str", None]:
        return self.buy_condition(input_data, stock) or self.sell_condition(
            input_data, stock
        )


class SVCStrategy(Strategy):
    def __init__(self, data: dict):
        self.models = {}
        for key, val in data.items():
            try:
                self.models[key] = SVC(random_state=123).fit(
                    val.get("X_train"), val.get("y_train")
                )
            except ValueError:
                print(val.get("X_train"))

    def execute(self, input_data: dict, stock: str) -> str:
        prediction = self.models[stock].predict([input_data.get("input_data")])
        if bool(prediction):
            return "buy"
        return "sell"


class TSRFStrategy(Strategy):
    def __init__(self, data: dict):
        self.models = {}
        for key, val in data.items():
            self.models[key] = TimeSeriesForest(random_state=123).fit(
                val.get("X_train"), val.get("y_train")
            )

    def execute(self, input_data: dict, stock: str) -> str:
        prediction = self.models[stock].predict([input_data.get("input_data")])
        if bool(prediction):
            return "buy"
        return "sell"



class ARIMAStrategy(Strategy):
    def __init__(self, data: dict):
        self.models = {}
        self.trend = {}
        self.data = {}
        for key, val in data.items():
            self.models[key] = ARIMA(list(val.get("prices")), order=(0, 1, 2)).fit()
            self.data[key] = list(val.get("prices"))

    def execute(self, input_data: dict, stock: str) -> str:
        output = self.models[stock].forecast()[0]
        self.data[stock].append(input_data.get("price"))
        self.models[stock] = ARIMA(self.data[stock], order=(0, 1, 2)).fit()
        if output > input_data.get("price"):
            return "buy"
        return "sell"
