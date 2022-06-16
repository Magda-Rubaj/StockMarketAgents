from indicators import make_decisions_table
import yfinance as yf
import pandas as pd


df = pd.DataFrame() 
df = yf.Ticker("^gspc")
df = df.history(start='2021-01-03', end='2021-09-20', interval="1h")

def simulate():
    starting_money = 10000
    table = make_decisions_table(df)
    for index, value in table.iterrows():
        if value['macd'] == 'buy':
            starting_money -= 0.3 * value['price']
        elif value['macd'] == 'sell':
            starting_money += 0.3 * value['price']

    print(starting_money)

simulate()