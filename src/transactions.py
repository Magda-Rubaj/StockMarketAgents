from dataclasses import dataclass
from typing import Literal
from indicators import make_decisions_table
from datetime import datetime
import yfinance as yf
import pandas as pd



def calculate_df(symbol):
    df = pd.DataFrame()
    df = yf.Ticker(symbol)
    df = df.history(start='2021-10-03', end='2022-01-05', interval="1h")
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
        print(self.position, self.budget)
        self.position = None
    
    def open_position(self, price, type):
        self.position = Position(
            symbol="^gspc",
            number=self.calculate_shares(price),
            type=type,
            opening_price=price
        )
        if type == 'buy':
            self.buy_signal = False
        elif type == 'sell':
            self.sell_signal = False
        return "opened"

    def check_buy(self, value):
        if value['macd'] == 'buy':
            self.buy_signal = True

        if self.buy_signal and value['stochastic'] == "oversold":
            if self.position and self.position.type == 'sell':
                self.close_position(value['price'],)
                return "closed"
            return self.open_position(value['price'], 'buy')

    def check_sell(self, value):
        if value['macd'] == 'sell':
            self.sell_signal = True

        if self.sell_signal and value['stochastic'] == "overbought":
            if self.position and self.position.type == 'buy':
                self.close_position(value['price'])
                return "closed"
            return self.open_position(value['price'], 'sell')
    
    def stop_loss(self, value):
        if self.calculate_return(value['price']) / self.budget < 0.8:
            print(self.budget, self.calculate_return(value['price']) / self.budget)
            self.close_position(value['price'])
            return "closed"


class Simulator:

    def __init__(self):
        self.chosen_stock = None
        self.budget = 10000
    
    def chose_stock(self, df_dict, agent):
        lnt = len(df_dict["^gspc"])
        for i in range(lnt):
            for k, v in df_dict.items():
                if agent.check_sell(v.iloc[i]) == "opened" or agent.check_buy(v.iloc[i]) == "opened":
                    self.chosen_stock = k
                    return

    def simulate(self):
        agent = DecisionAgent()
        possibilities = ["^gspc", "fb", "tsla"]
        df_dict = {p: make_decisions_table(calculate_df(p)) for p in possibilities}

        self.chose_stock(df_dict, agent)
        lnt = len(df_dict["^gspc"])
        for i in range(lnt):
            if (agent.check_buy(
                df_dict[self.chosen_stock].iloc[i]) == "closed" 
                or agent.check_sell(df_dict[self.chosen_stock].iloc[i]) == "closed"
                #or agent.stop_loss(df_dict[self.chosen_stock].iloc[i]) == "closed"
            ):
                self.chose_stock(df_dict, agent)
        print(agent.budget)




simulator = Simulator()
simulator.simulate()
