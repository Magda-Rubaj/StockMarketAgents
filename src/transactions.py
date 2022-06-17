from dataclasses import dataclass
from typing import Literal
from indicators import make_decisions_table
import yfinance as yf
import pandas as pd


df = pd.DataFrame()
df = yf.Ticker("^gspc")
df = df.history(start='2020-01-03', end='2021-09-30', interval="1d")


@dataclass
class Position:
    symbol: str
    number: float
    type: Literal["buy", "sell"]


@dataclass
class Portfolio:
    positions_opened: Position


class Simulator:

    def __init__(self):
        self.budget = 10000
        self.buy_signal = False
        self.sell_signal = False
        self.indicator_first = None
    
    def check_buy(self, value):
        if value['macd'] == 'buy':
            self.buy_signal = True

        if self.buy_signal and value['stochastic'] == "oversold":
            self.budget -= 0.3 * value['price']
            self.buy_signal = False

    def check_sell(self, value):
        if value['macd'] == 'sell':
            self.sell_signal = True
        
        if self.sell_signal and value['stochastic'] == "overbought":
            self.budget += 0.3 * value['price']
            self.sell_signal = False


    def simulate(self):
        table = make_decisions_table(df)
        for index, value in table.iterrows():
            self.check_buy(value)
            self.check_sell(value)
        print(self.budget)


simulator = Simulator()
simulator.simulate()
