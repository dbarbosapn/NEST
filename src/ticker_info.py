import yfinance as yf
import pandas as pd
import sys

ticker_map = {"S&P 500": "VOO"}


def get_info(ticker, start=None, end=None):
    t = yf.Ticker(ticker if ticker not in ticker_map else ticker_map[ticker])
    if start is not None and end is not None:
        history = t.history(start=start, end=end)
    else:
        history = t.history(period="6mo")

    return history


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {} <TICKER>".format(
            sys.argv[0]))
        exit()

    ticker = sys.argv[1]
    history = get_info(ticker)
    print(history)
