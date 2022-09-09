from pyts.classification import TimeSeriesForest
from abc import ABC, abstractmethod


class AbstractStrategy(ABC):
    @abstractmethod
    def execute(value):
        raise NotImplementedError


class RSIEMACrossoverStrategy(AbstractStrategy):
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

    def execute(self, value):
        return self.buy_condition(value) or self.sell_condition(value["ema"])


class MachineLearningStrategy(AbstractStrategy):
    def __init__(self, data):
        self.models = {}
        for key, val in data:
            self.models[key] = TimeSeriesForest(random_state=123).fit(val.get("train_X"), val.get("train_y"))

    def execute(self, value):
        prediction = self.model.predict([value])
        if bool(prediction):
            return "buy"
        else:
            return "sell"