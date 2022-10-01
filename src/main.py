import argparse
import random

from data import get_data, get_initial_df
from strategies import (ARIMAStrategy, EMACrossoverStrategy,
                        MachineLearningStrategy)
from agents import Agent


class App:
    def add_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--start-date", required=True)
        parser.add_argument("--end-date", required=True)
        parser.add_argument("--stocks-number")
        self.args = parser.parse_args()

    def _init_agents(self, stocks):
        agents = []

        arima_data = {}
        arima_train = {}

        ml_data = {}
        ml_train = {}

        ema_data = {}

        for stock in stocks:
            initial_df = get_initial_df(stock, self.args.start_date, self.args.end_date)
            ml_train[stock], ml_data[stock] = get_data(initial_df, "ml")
            ema_data[stock] = get_data(initial_df,"ema")
            arima_train[stock], arima_data[stock] = get_data(initial_df,"arima")
        ml_strategy = MachineLearningStrategy(ml_train)
        arima_strategy = ARIMAStrategy(arima_train)
        ema_strategy = EMACrossoverStrategy(ema_data, stocks)
        agents.append(Agent(ml_strategy, ml_data, "ML"))
        agents.append(Agent(ema_strategy, ema_data, "EMA"))
        agents.append(Agent(arima_strategy, arima_data, "ARIMA"))
        return agents
    

    def main(self):
        possible_stocks = ["tsla", "amzn", "fdx", "amd", "nvda", "ko"]
        stocks = random.sample(possible_stocks, int(self.args.stocks_number))
        agents = self._init_agents(stocks)
        for agent in agents:
            agent.simulate()
            print(agent.name)

if __name__ == "__main__":
    app = App()
    app.add_args()
    app.main()
