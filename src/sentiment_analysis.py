from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import json
import sys
from datetime import datetime
from dateutil import parser


def load_data(ticker, from_year, start_month, to_year, end_month, data_location):
    data = []
    for y in range(from_year, to_year + 1):
        s = 1
        e = 12
        if y == from_year:
            s = start_month
        if y == to_year:
            e = end_month

        for m in range(s, e + 1):
            with open("{}/{}/{}-{}-{}.json".format(data_location, ticker, ticker, m, y), "r") as f:
                j = json.load(f)
                for entry in j['entries']:
                    title = " - ".join(entry['title'].split(" - ")[:-1])
                    date = parser.parse(entry['published'])
                    if date.year == y and date.month == m:
                        data.append([entry['published'], title])
    df = pd.DataFrame(data, columns=['date', 'title'])
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.normalize()
    df = df.sort_values(by='date')
    df['date'] = df['date'].dt.tz_convert(None)
    df.set_index('date', inplace=True)
    return df


def evaluate_data(ticker, from_year, start_month, to_year, end_month, data_location, out=False):
    data = load_data(ticker, from_year, start_month,
                     to_year, end_month, data_location)
    scores = []
    vader = SentimentIntensityAnalyzer()
    for i in range(0, len(data['title'])):
        scores.append(evaluate(vader, data['title'][i]))
    data['score'] = scores
    if out:
        data.to_csv("output/{}-eval.csv".format(ticker))
    return data


def evaluate(vader, text):
    sentiment = vader.polarity_scores(text)
    return sentiment['compound']


def monthly_mean(data):
    curr_month = data.index[0].month
    curr_year = data.index[0].year
    acc = 0
    counter = 0
    means = []
    dates = []
    for i in range(0, len(data.index)):
        m = data.index[i].month
        y = data.index[i].year

        if i == len(data.index) - 1:
            counter += 1
            acc += data['score'][i]
            means.append(acc / counter)
            dates.append("{}-{}-01".format(curr_year, curr_month))
            break

        if m != curr_month:
            if counter > 0:
                means.append(acc / counter)
                dates.append("{}-{}-01".format(curr_year, curr_month))
            acc = 0
            counter = 0
            curr_month = m
            curr_year = y
        else:
            counter += 1
            acc += data['score'][i]
    df = pd.DataFrame(list(zip(dates, means)), columns=['date', 'score'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python {} <TEXT>".format(
            sys.argv[0]))
        exit()

    text = sys.argv[1]
    vader = SentimentIntensityAnalyzer()
    print(evaluate(vader, text))
