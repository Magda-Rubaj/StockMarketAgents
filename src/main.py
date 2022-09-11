from transactions import Agent
from strategies import MachineLearningStrategy
from data import get_initial_df, get_ml_df

class App:
    
    def _get_ml_data(self, initial_df):
        X, y, prices = get_ml_df(initial_df, 20)
        split = int(0.8*len(initial_df))
        data = {
            "X_train": X[:split],
            "y_train": y[:split],
            "X_test": X[split:],
            "y_test": y[split:],
            "prices": prices[split:]
        }
        return data


    def _init_agents(self, ml_data):
        agents = []
        ml_strategy = MachineLearningStrategy(ml_data)
        agents.append(Agent(ml_strategy, ml_data))
        return agents
    

    def main(self):
        stocks = ["xom", "tsla", "^gspc"]
        loop_data = {}
        for stock in stocks:
            initial_df = get_initial_df(stock, "2016-08-01", "2022-08-01")
            loop_data[stock] = self._get_ml_data(initial_df)
        #print(loop_data)
        agents = self._init_agents(loop_data)
        for agent in agents:
            agent.simulate()

if __name__ == "__main__":
    App().main()