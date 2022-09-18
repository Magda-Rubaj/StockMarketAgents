from transactions import Agent
from strategies import MachineLearningStrategy, ARIMAStrategy, EMACrossoverStrategy
from data import get_initial_df, get_data

class App:

    def _init_agents(self, stocks):
        agents = []

        arima_data = {}
        arima_train = {}

        ml_data = {}
        ml_train = {}

        ema_data = {}

        for stock in stocks:
            initial_df = get_initial_df(stock, "2016-08-01", "2022-09-01")
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
        stocks = ["xom", "tsla", "^gspc"]
        agents = self._init_agents(stocks)
        for agent in agents:
            agent.simulate()
            print(agent.name)

if __name__ == "__main__":
    App().main()