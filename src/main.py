from transactions import Agent, Simulation
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
        ml_strategy = MachineLearningStrategy(ml_data.get("X_train"), ml_data.get("y_train"))
        agents.append(Agent(ml_strategy, ml_data.get("X_test")))
        return agents
    

    def main(self):
        stock = "xom"
        initial_df = get_initial_df(stock, "2016-08-01", "2022-08-01")
        ml_df = self._get_ml_data(initial_df)
        agents = self._init_agents(ml_df)
        simulation = Simulation()
        simulation.simulate(ml_df.get("prices"), agents, stock)

if __name__ == "__main__":
    App().main()