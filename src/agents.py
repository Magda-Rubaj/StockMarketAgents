from dataclasses import dataclass
from strategies import Strategy
from typing import Literal
import pandas as pd


@dataclass
class Position:
    symbol: str
    number: float
    type: Literal["buy", "sell"]
    opening_price: float


class Agent:
    def __init__(self, strategy: Strategy, data, name: str, budget: float = 10000.0):
        self.name = name
        self.strategy = strategy
        self.data = data
        self.portfolio = {}
        self.budget = budget

    def calculate_shares(self, price: float):
        portfolio_entries = len(list(self.data.keys()))
        return round(self.budget / price / portfolio_entries, 1)

    def calculate_return(self, current_price: float, symbol: str) -> float:
        if not self.portfolio.get(symbol):
            return
        if self.portfolio.get(symbol).type == "buy":
            return self.budget + self.portfolio.get(symbol).number * (
                current_price - self.portfolio.get(symbol).opening_price
            )
        elif self.portfolio.get(symbol).type == "sell":
            return self.budget + self.portfolio.get(symbol).number * (
                self.portfolio.get(symbol).opening_price - current_price
            )

    def close_position(self, current_price: float, symbol: str):
        self.budget = self.calculate_return(current_price, symbol)
        self.portfolio[symbol] = None

    def open_position(self, price: float, type: str, symbol: str):
        if self.portfolio.get(symbol):
            return

        self.portfolio[symbol] = Position(
            symbol=symbol,
            number=self.calculate_shares(price),
            type=type,
            opening_price=price,
        )

    def action(self, value: dict, stock: str):
        self.check_stop_loss(value.get("price"), stock)
        action = self.strategy.execute(value, stock)
        if pd.isna(value.get("price")):
            return
        if self.portfolio.get(stock):
            if self.portfolio.get(stock).type == "sell" and action == "buy":
                self.close_position(value.get("price"), stock)
                self.open_position(value.get("price"), "buy", stock)
                print(f"{self.name} OPENED BUY CLOSED SELL POSITION ON{stock}")

            elif self.portfolio.get(stock).type == "buy" and action == "sell":
                self.close_position(value.get("price"), stock)
                self.open_position(value.get("price"), "sell", stock)
                print(f"{self.name} OPENED SELL CLOSED BUY POSITION ON{stock}")
        else:
            if action == "buy":
                self.open_position(value.get("price"), "buy", stock)
                print(f"{self.name} OPENED BUY")
            elif action == "sell":
                self.open_position(value.get("price"), "sell", stock)
                print(f"{self.name} OPENED SELL")

    def check_stop_loss(self, price: float, stock: str):
        returned = self.calculate_return(price, stock)
        if returned and (returned / self.budget < 0.85):
            self.close_position(price, stock)

    def simulate(self):
        for stock in self.data.keys():
            data = self.data[stock]
            for entry in data:
                self.action(entry, stock)
