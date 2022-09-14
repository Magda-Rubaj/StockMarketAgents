from transactions import Agent
from strategies import MachineLearningStrategy
from data import get_initial_df, get_ml_df

class App:
    
    def _get_ml_data(self, initial_df):
        X, y, prices = get_ml_df(initial_df, 20)
        split = int(0.8*len(initial_df))
        
        train_data = {
            "X_train": X[:split],
            "y_train": y[:split]
        }
        loop_data = [{
            "input_data": X.iloc[i],
            "price": prices[i]
        } for i in range(len(prices[split:]))]
        return train_data, loop_data


    def _init_agents(self, train_data, loop_data):
        agents = []
        ml_strategy = MachineLearningStrategy(train_data)
        agents.append(Agent(ml_strategy, loop_data))
        return agents
    

    def main(self):
        stocks = ["xom", "tsla", "^gspc"]
        loop_data = {}
        train_data = {}
        for stock in stocks:
            initial_df = get_initial_df(stock, "2016-08-01", "2022-08-01")
            ml_data = self._get_ml_data(initial_df)
            loop_data[stock] = ml_data[1]
            train_data[stock] = ml_data[0]
        agents = self._init_agents(train_data, loop_data)
        for agent in agents:
            agent.simulate()

if __name__ == "__main__":
    App().main()