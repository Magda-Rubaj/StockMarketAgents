import argparse
import os
import pandas as pd
import asyncio
import random
from typing import List

from agents import Agent
from data import get_data, get_df_from_api
from logger import logger
from strategies import (ARIMAStrategy, EMACrossoverStrategy,
                        SVCStrategy, TSRFStrategy)


class App:

    def add_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--start-date", required=False)
        parser.add_argument("--end-date", required=False)
        parser.add_argument("--interval", required=False, choices=["30m" ,"60m" ," 90m", "1h", "1d", "5d", "1wk", "1mo"])
        parser.add_argument("--stocks-number", required=False)
        parser.add_argument("--benchmark", action='store_true')
        self.args = parser.parse_args()

    def _init_agents_cli(self, stocks: List[str]) -> List[Agent]:
        agents = []

        arima_data = {}
        arima_train = {}

        tsrf_data = {}
        tsrf_train = {}
        
        svc_data = {}
        svc_train = {}

        ema_data = {}

        for stock in stocks:
            initial_df = get_df_from_api(stock, self.args.start_date, self.args.end_date, self.args.interval)
            tsrf_train[stock], tsrf_data[stock] = get_data(initial_df, "tsrf")
            svc_train[stock], svc_data[stock] = get_data(initial_df, "svc")
            ema_data[stock] = get_data(initial_df,"ema")
            arima_train[stock], arima_data[stock] = get_data(initial_df,"arima")
        tsrf_strategy = TSRFStrategy(tsrf_train)
        svc_strategy = SVCStrategy(svc_train)
        arima_strategy = ARIMAStrategy(arima_train)
        ema_strategy = EMACrossoverStrategy(ema_data, stocks)
        agents.append(Agent(tsrf_strategy, tsrf_data, "TSRF"))
        agents.append(Agent(svc_strategy, svc_data, "SVC"))
        agents.append(Agent(ema_strategy, ema_data, "EMA"))
        agents.append(Agent(arima_strategy, arima_data, "ARIMA"))
        return agents
    
    def _init_agents_files(self):
        intervals = ["1wk", "1d", "5d"]
        for interval in intervals:
            arima_data = {}
            arima_train = {}

            tsrf_data = {}
            tsrf_train = {}
            
            svc_data = {}
            svc_train = {}

            ema_data = {}
            files = [f for f in os.listdir('./csv')]
            files = [file for file in files if interval in file]
            means = {"arima": 0, "svc": 0, "tsrf": 0}
            for file in files:
                initial_df  = pd.read_csv(f"csv/{file}")
                initial_df["Close"] = initial_df["Close"].fillna(method="ffill")
                stock = file.split("_")[0]
                tsrf_train[stock], tsrf_data[stock] = get_data(initial_df, "tsrf")
                svc_train[stock], svc_data[stock] = get_data(initial_df, "svc")
                ema_data[stock] = get_data(initial_df,"ema")
                arima_train[stock], arima_data[stock] = get_data(initial_df,"arima")
                tsrf_strategy = TSRFStrategy(tsrf_train)
                svc_strategy = SVCStrategy(svc_train)
                arima_strategy = ARIMAStrategy(arima_train)
                #ema_strategy = EMACrossoverStrategy(ema_data, stocks)
                means["tsrf"] += Agent(tsrf_strategy, tsrf_data, "TSRF").simulate()
                means["svc"] += Agent(svc_strategy, svc_data, "SVC").simulate()
                #agents.append(Agent(ema_strategy, ema_data, "EMA"))
                means["arima"] += Agent(arima_strategy, arima_data, "ARIMA").simulate()
            
            for key, val in means.items():
                val = val / len(files)
                logger.info(f"interval: {interval} | strategy: {key} | mean: {val}")
    
    

    async def main(self):
        if self.args.benchmark:
            self._init_agents_files()
        else:
            possible_stocks = ["tsla", "amzn", "fdx", "amd", "nvda", "ko"]
            stocks = random.sample(possible_stocks, int(self.args.stocks_number))
            agents = self._init_agents_cli(stocks)
            coroutines = [agent.simulate() for agent in agents]
            results = await asyncio.gather(*coroutines)
        

if __name__ == "__main__":
    app = App()
    app.add_args()
    asyncio.run(app.main())
