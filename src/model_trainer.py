import sentiment_analysis
import ticker_info
import sys
import model_visualizer
import threading
import time
import pandas as pd
import NEAT
from datetime import datetime, timedelta
from subject import Subject
import neat
import os
import pickle


trainingData = None
pop = None
disableGraphics = False
BASE_BUDGET = 250


def get_training_data(ticker, from_year, to_year):
    global training_data
    t = ticker_info.get_info(
        ticker, "{}-01-01".format(from_year), "{}-12-31".format(to_year))
    all_ticker_data = t[['Close', 'Volume']]
    ticker_data = normalize_stock_data(all_ticker_data)

    s = sentiment_analysis.evaluate_data(
        ticker, from_year, 1, to_year, 12, "data/training/news")
    s = normalize_sentiment_data(s)
    sentiment_data = sentiment_analysis.monthly_mean(s)

    training_data = (all_ticker_data, ticker_data, sentiment_data)


def train(subjects):
    global training_data
    (all_ticker_data, ticker_data, sentiment_data) = training_data
    curr_index = 120
    t0 = time.clock()
    last_m = all_ticker_data.index[0].month
    for i in range(0, len(all_ticker_data.index)):
        if not disableGraphics:
            model_visualizer.add_point(
                all_ticker_data.index[i], all_ticker_data['Close'][i])
        if i >= curr_index:
            stock, sentiment = get_final_data(
                ticker, ticker_data, sentiment_data, curr_index, from_year)
            close_data = stock['Close'].tolist()
            volume_data = stock['Volume'].tolist()
            news_data = sentiment['score'].tolist()

            data = []
            data.extend(news_data)
            data.extend(volume_data)
            data.extend(close_data)

            today_data = all_ticker_data.iloc[curr_index]
            curr_price = today_data['Close']
            today = all_ticker_data.index[curr_index]
            curr_m = today.month

            for s in subjects:
                if curr_m != last_m:
                    s.notify_budget_cycle()
                    last_m = curr_m
                val = s.evaluate(data, curr_price)[0]
                if val > 0:
                    s.buy(val, curr_price, today)
                elif val < 0:
                    s.sell(-val, curr_price, today)

            curr_index += 1

    if not disableGraphics:
        model_visualizer.reset()
    print("Total Time: ", time.clock() - t0)


def normalize_stock_data(data):
    ticker_data = data.copy(deep=True)
    ticker_data['Close'] = ticker_data['Close'].pct_change()
    ticker_data.iloc[0, 0] = 0
    ticker_data['Volume'] = ticker_data['Volume'].pct_change()
    ticker_data.iloc[0, 1] = 0

    min_close = ticker_data['Close'].min(axis=0)
    max_close = ticker_data['Close'].max(axis=0)
    ticker_data['Close'] = (ticker_data['Close'] -
                            min_close) / (max_close - min_close)

    min_volume = ticker_data['Volume'].min(axis=0)
    max_volume = ticker_data['Volume'].max(axis=0)
    ticker_data['Volume'] = (ticker_data['Volume'] -
                             min_volume) / (max_volume - min_volume)

    return ticker_data


def normalize_sentiment_data(data):
    min_score = data['score'].min(axis=0)
    max_score = data['score'].max(axis=0)
    data['score'] = (data['score'] -
                     min_score) / (max_score - min_score)
    return data


def get_final_data(ticker, ticker_data, sentiment_data, curr_index, b_year):
    stock = ticker_data.iloc[curr_index-120:curr_index]
    s_index0 = (stock.index[0].year - b_year)*12 + stock.index[0].month - 1
    s_index1 = (stock.index[-1].year - b_year)*12 + stock.index[-1].month
    if s_index1 - s_index0 > 6:
        s_index0 += 1
    sentiment = sentiment_data.iloc[s_index0:s_index1]
    return stock, sentiment


def eval_genomes(genomes, config):
    global pop

    subjects = {}

    for genome_id, genome in genomes:
        subjects[genome_id] = Subject(genome, config, BASE_BUDGET, 0.0015)

    train(subjects.values())

    if pop.best_genome is not None:
        print("##################################")
        print("Operations:")
        print(subjects[pop.best_genome.key].operations)
        print("Total Sold:")
        print(subjects[pop.best_genome.key].total_sold)
        print("Total Spent:")
        print(subjects[pop.best_genome.key].total_spent)
        print("Profit:")
        print(subjects[pop.best_genome.key].get_realized_profit())


def start_training():
    global pop
    pop.run(eval_genomes)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python {} <TICKER> <FROM_YEAR> <TO_YEAR> <DISABLE_GRAPHICS>".format(
            sys.argv[0]))
        exit()

    ticker = sys.argv[1]
    from_year = int(sys.argv[2])
    to_year = int(sys.argv[3])
    disableGraphics = len(sys.argv) >= 4

    get_training_data(ticker, from_year, to_year)

    if os.path.exists("models/{}.bin".format(ticker)):
        with open("models/{}.bin".format(ticker), "rb") as f:
            pop = pickle.load(f)
    else:
        pop = NEAT.init()

    tmain = threading.Thread(target=start_training, daemon=True)
    tmain.start()
    if not disableGraphics:
        model_visualizer.start("{} (Training)".format(ticker))
    else:
        print("Write 'S' to save or 'Q' to quit (ENTER at the end)")
        while True:
            i = input()
            if i == "q":
                exit()
            elif i == "s":
                old_threshold = pop.config.fitness_threshold
                pop.config.fitness_threshold = -1
                tmain.join()
                pop.config.fitness_threshold = old_threshold
                with open("models/{}.bin".format(ticker), "wb") as f:
                    pickle.dump(pop, f)
                break
