from dataclasses import dataclass
from typing import Literal
import random
from indicators import make_decisions_table
from datetime import datetime
import yfinance as yf
import pandas as pd



def calculate_df(symbol):
    df = pd.DataFrame()
    df = yf.Ticker(symbol)
    df = df.history(start='2022-01-01', end='2022-06-30', interval="1h")
    return df


@dataclass
class Position:
    symbol: str
    number: float
    type: Literal["buy", "sell"]
    opening_price: float


@dataclass
class Portfolio:
    positions_opened: Position


class DecisionAgent:

    def __init__(self):
        self.buy_signal = False
        self.sell_signal = False
        self.position = None
        self.budget = 10000
    
    def calculate_shares(self, price):
        return round(self.budget / price * 3 / 4, 1)
    
    def calculate_return(self, current_price):
        if not self.position:
            return
        if self.position.type == 'buy':
            return self.budget + self.position.number * \
                (current_price - self.position.opening_price)
        elif self.position.type == 'sell':
            return self.budget + self.position.number * \
                (self.position.opening_price - current_price)
    
    def close_position(self, current_price):
        self.budget = self.calculate_return(current_price)
        self.position = None
        return "closed"
    
    def open_position(self, price, type, symbol):
        if self.position:
            return

        self.position = Position(
            symbol=symbol,
            number=self.calculate_shares(price),
            type=type,
            opening_price=price
        )
        if type == 'buy':
            self.buy_signal = False
        elif type == 'sell':
            self.sell_signal = False
        return "opened"

    def check_buy(self, value, symbol=None):
        if value['macd'] == 'buy':
            if self.position and self.position.type == 'sell':
                return "close"
            self.buy_signal = True

        if self.buy_signal and value['stochastic'] == "oversold":
            return "open"
    
    def buy(self, value, symbol=None):
        if self.check_buy(value, symbol) == 'close':
            return self.close_position(value['price'])
        if self.check_buy(value, symbol) == 'open':
            return self.open_position(value['price'], 'buy', symbol)
    
    def sell(self, value, symbol=None):
        if self.check_sell(value, symbol) == 'close':
            return self.close_position(value['price'])
        if self.check_sell(value, symbol) == 'open':
            return self.open_position(value['price'], 'sell', symbol)


    def check_sell(self, value, symbol=None):
        if value['macd'] == 'sell':
            if self.position and self.position.type == 'buy':
                return "close"
            self.sell_signal = True

        if self.sell_signal and value['stochastic'] == "overbought":
            return "open"
    
    def stop_loss(self, value):
        returned = self.calculate_return(value['price'])
        if returned and (returned / self.budget < 0.85):
            return self.close_position(value['price'])


class Simulator:

    def __init__(self):
        self.chosen_stock = None
        self.budget = 10000
    
    def chose_stock(self, df_dict, start):
        lnt = len(df_dict["^gspc"])
        #start = start + 1 if (start < lnt - 10) else start
        for i in range(start+1, lnt):
            for k, v in df_dict.items():
                try:
                    if v.iloc[i]['macd'] in ['sell', 'buy']:
                        self.chosen_stock = k
                        print(k)
                        return
                except IndexError:
                    break

    def simulate(self):
        agent = DecisionAgent()
        possibilities = ["fb", "^gspc", "tsla"]
        df_dict = {p: make_decisions_table(calculate_df(p)) for p in possibilities}

        self.chose_stock(df_dict, 0)
        lnt = len(df_dict["^gspc"])
        for i in range(lnt):
            if (
                agent.buy(df_dict[self.chosen_stock].iloc[i], self.chosen_stock) == "closed" 
                or agent.sell(df_dict[self.chosen_stock].iloc[i], self.chosen_stock) == "closed"
                or agent.stop_loss(df_dict[self.chosen_stock].iloc[i]) == "closed"
            ):
                self.chose_stock(df_dict, i)
        print(agent.budget)




simulator = Simulator()
simulator.simulate()
