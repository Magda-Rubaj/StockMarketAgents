from dataclasses import dataclass
from typing import Literal
import random
from indicators import make_decisions_table, RSIEMACrossoverStrategy
from datetime import datetime
import yfinance as yf
import pandas as pd


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

    def __init__(self, strategy: RSIEMACrossoverStrategy = RSIEMACrossoverStrategy()):
        self.strategy = strategy
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
    
    def action(self, value, stock):
        action = self.strategy.execute(value["price"], value["ema"])
        if self.position:
            if self.position.type == "sell" and action == "buy":
                self.close_position(value["price"])
                self.open_position(value["price"], "buy", stock)
                print("OPENED BUY CLOSED SELL")
            
            elif self.position.type == "buy" and action == "sell":
                self.close_position(value["price"])
                self.open_position(value["price"], "sell", stock)
                print("OPENED SELL CLOSED BUY")
        else:
            if action == "buy":
                self.open_position(value["price"], "buy", stock)
                print("OPENED BUY")
            elif action == "sell":
                self.open_position(value["price"], "sell", stock)
                print("OPENED SELL")
        print(value)
        print(self.budget)


    def stop_loss(self, value):
        returned = self.calculate_return(value['price'])
        if returned and (returned / self.budget < 0.85):
            return self.close_position(value['price'])


class Simulator:

    def __init__(self):
        self.chosen_stock = "^gspc"
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
        possibilities = ["^gspc"]
        df_dict = {p: make_decisions_table(calculate_df(p)) for p in possibilities}
        print(df_dict["^gspc"])
        #self.chose_stock(df_dict, 0)
        lnt = len(df_dict["^gspc"])
        agent.strategy.first_value(df_dict[self.chosen_stock].iloc[0]["price"], df_dict[self.chosen_stock].iloc[0]["ema"])
        for i in range(1, lnt):
            agent.action(df_dict[self.chosen_stock].iloc[i], self.chosen_stock)
            # if (
            #     agent.buy(df_dict[self.chosen_stock].iloc[i], self.chosen_stock) == "closed" 
            #     or agent.sell(df_dict[self.chosen_stock].iloc[i], self.chosen_stock) == "closed"
            #     or agent.stop_loss(df_dict[self.chosen_stock].iloc[i]) == "closed"
            # ):
            #     self.chose_stock(df_dict, i)
        print(agent.budget)




simulator = Simulator()
simulator.simulate()
