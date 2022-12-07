import argparse
from data import get_df_from_api


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--interval", required=True)
    parser.add_argument("--symbols", required=True)
    return parser.parse_args()


def save_df(df, symbol, interval, start):
    df.to_csv(f"csv/{symbol}_{interval}_{start}.csv", index=False)


def dataframes_to_files():
    args = get_args()
    symbols = args.symbols.split(",")
    for symbol in symbols:
        df = get_df_from_api(symbol, args.start_date, args.end_date, args.interval)
        save_df(df, symbol, args.interval, args.start_date)


if __name__ == "__main__":
    dataframes_to_files()