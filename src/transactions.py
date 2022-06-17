from dataclasses import dataclass
from typing import Literal
from indicators import make_decisions_table
import yfinance as yf
import pandas as pd


df = pd.DataFrame()
df = yf.Ticker("^gspc")
df = df.history(start='2021-01-03', end='2021-12-15', interval="1h")


@dataclass
class Position:
    symbol: str
    number: float
    type: Literal["buy", "sell"]
    opening_price: float


@dataclass
class Portfolio:
    positions_opened: Position


class Simulator:

    def __init__(self):
        self.budget = 10000
        self.buy_signal = False
        self.sell_signal = False
        self.position = None
    
    def close_position(self, current_price):
        if self.position.type == 'buy':
            self.budget += self.position.number * (current_price - self.position.opening_price)
        elif self.position.type == 'sell':
            self.budget += self.position.number * (self.position.opening_price - current_price)
        print(self.budget, self.position.type)
        self.position = None
        
    
    def check_buy(self, value):
        if value['macd'] == 'buy':
            self.buy_signal = True

        if self.buy_signal and value['stochastic'] == "oversold":
            if self.position and self.position.type == 'sell':
                self.close_position(value['price'])
                return

            self.position = Position(
                symbol="^gspc",
                number=0.8,
                type='buy',
                opening_price=value['price']
            )
            self.buy_signal = False

    def check_sell(self, value):
        if value['macd'] == 'sell':
            self.sell_signal = True
        
        if self.sell_signal and value['stochastic'] == "overbought":
            if self.position and self.position.type == 'buy':
                self.close_position(value['price'])
                return
            self.position = Position(
                symbol="^gspc",
                number=0.8,
                type='sell',
                opening_price=value['price']
            )
            self.sell_signal = False


    def simulate(self):
        table = make_decisions_table(df)
        for index, value in table.iterrows():
            self.check_buy(value)
            self.check_sell(value)
        print(self.budget)


simulator = Simulator()
simulator.simulate()
