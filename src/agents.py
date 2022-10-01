from dataclasses import dataclass
from typing import Literal
import pandas as pd



@dataclass
class Position:
    symbol: str
    number: float
    type: Literal["buy", "sell"]
    opening_price: float


class Agent:
    def __init__(self, strategy, data, name, budget=10000):
        self.name = name
        self.strategy = strategy
        self.data = data
        self.portfolio = {}
        self.budget = budget
    
    def calculate_shares(self, price):
        return round(self.budget / price / len(list(self.data.keys())), 1)
    
    def calculate_return(self, current_price, symbol):
        if not self.portfolio.get(symbol):
            return
        if self.portfolio.get(symbol).type == 'buy':
            return self.budget + self.portfolio.get(symbol).number * \
                (current_price - self.portfolio.get(symbol).opening_price)
        elif self.portfolio.get(symbol).type == 'sell':
            return self.budget + self.portfolio.get(symbol).number * \
                (self.portfolio.get(symbol).opening_price - current_price)
    
    def close_position(self, current_price, symbol):
        self.budget = self.calculate_return(current_price, symbol)
        self.portfolio[symbol] = None
        return "closed"
    
    def open_position(self, price, type, symbol):
        if self.portfolio.get(symbol):
            return

        self.portfolio[symbol] = Position(
            symbol=symbol,
            number=self.calculate_shares(price),
            type=type,
            opening_price=price
        )
    
    def action(self, value, stock):
        action = self.strategy.execute(value, stock)
        if pd.isna(value.get("price")):
            return
        if self.portfolio.get(stock):
            if self.portfolio.get(stock).type == "sell" and action == "buy":
                self.close_position(value.get("price"), stock)
                self.open_position(value.get("price"), "buy", stock)
                #print("OPENED BUY CLOSED SELL")
            
            elif self.portfolio.get(stock).type == "buy" and action == "sell":
                self.close_position(value.get("price"), stock)
                self.open_position(value.get("price"), "sell", stock)
                #print("OPENED SELL CLOSED BUY")
        else:
            if action == "buy":
                self.open_position(value.get("price"), "buy", stock)
                #print("OPENED BUY")
            elif action == "sell":
                self.open_position(value.get("price"), "sell", stock)
                #print("OPENED SELL")

    def check_stop_loss(self, value):
        returned = self.calculate_return(value.get("price"))
        if returned and (returned / self.budget < 0.85):
            return self.close_position(value.get("price"))
        
    
    def simulate(self):
        first_key = list(self.data.keys())[0]
        data_len = len(self.data[first_key])
        for i in range(data_len):
            for stock in self.data.keys():
                data = self.data[stock]
                try:
                    self.action(data[i], stock)
                except IndexError:
                    pass
        print(self.budget)




