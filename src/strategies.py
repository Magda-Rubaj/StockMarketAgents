from pyts.classification import TimeSeriesForest
from statsmodels.tsa.arima.model import ARIMA
from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    @abstractmethod
    def execute(self, input_data):
        raise NotImplementedError


class RSIEMACrossoverStrategy(BaseStrategy):
    def __init__(self):
        #self.rsi_crossed = False
        self.ema_crossed = False
        self.is_above = -1

    def first_value(self, value):
        self.is_above = 1 if value["price"] > value["ema"] else 0

    def buy_condition(self, price, ema):
        if price > ema and not self.is_above:
            self.ema_crossed = True
            self.is_above = 1
            return "buy"
        return False

    def sell_condition(self, value):
        if value["price"] < value["ema"] and self.is_above:
            self.ema_crossed = True
            self.is_above = 0
            return "sell"
        return False

    def execute(self, input_data):
        return self.buy_condition(input_data) or self.sell_condition(input_data["ema"])


class MachineLearningStrategy(BaseStrategy):
    def __init__(self, data):
        self.models = {}
        for key, val in data.items():
            self.models[key] = TimeSeriesForest(random_state=123).fit(
                val.get("X_train"), val.get("y_train")
            )

    def execute(self, input_data, stock):
        prediction = self.models[stock].predict([input_data])
        if bool(prediction):
            return "buy"
        else:
            return "sell"


class ARIMAStrategy(BaseStrategy):
    def __init__(self, data):
        self.models = {}
        self.data = {}
        for key, val in data.items():
            self.models[key] = ARIMA(list(val.get("prices")), order=(0,1,2)).fit()
            self.data[key] = list(val.get("prices"))

    def execute(self, input_data, stock):
        output = self.models[stock].forecast()[0]
        self.data[stock].append(input_data)
        self.models[stock] = ARIMA(self.data[stock], order=(0,1,2)).fit()
        if output > input_data:
            return "buy"
        else:
            return "sell"
