from dataclasses import dataclass
from typing import Literal



@dataclass
class Position:
    symbol: str
    number: float
    type: Literal["buy", "sell"]
    opening_price: float


@dataclass
class Portfolio:
    positions_opened: Position


class Agent:
    def __init__(self, strategy, data, budget=10000):
        self.strategy = strategy
        self.data = data
        self.position = None
        self.budget = budget
    
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
    
    def action(self, value, index, stock):
        action = self.strategy.execute(self.decision_data.iloc[index])
        if self.position:
            if self.position.type == "sell" and action == "buy":
                self.close_position(value)
                self.open_position(value, "buy", stock)
                print("OPENED BUY CLOSED SELL")
            
            elif self.position.type == "buy" and action == "sell":
                self.close_position(value)
                self.open_position(value, "sell", stock)
                print("OPENED SELL CLOSED BUY")
        else:
            if action == "buy":
                self.open_position(value, "buy", stock)
                print("OPENED BUY")
            elif action == "sell":
                self.open_position(value, "sell", stock)
                print("OPENED SELL")
        # print(value)
        print(self.budget)


    def check_stop_loss(self, value):
        returned = self.calculate_return(value['price'])
        if returned and (returned / self.budget < 0.85):
            return self.close_position(value['price'])
        
    
    def simulate(self):
        first_key = self.data.keys()[0]
        princes_len = len(self.data[first_key]["prices"])
        for i in range(princes_len):
            for stock in self.data.keys():
                self.action(stock.get("prices")[i], i, stock)
        print(self.budget)




