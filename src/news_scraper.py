from pygooglenews import GoogleNews
from calendar import monthrange
from datetime import datetime
import pickle
import json
import sys
import os


def scrape(ticker, from_year, to_year, save_location):
    gn = GoogleNews(lang='en', country='US')
    today = datetime.today()
    cur_y = today.year
    cur_m = today.month

    for y in range(from_year, to_year+1):
        if y > cur_y:
            continue

        for m in range(1, 13):
            if y >= cur_y and m > cur_m:
                continue

            if not os.path.exists("{}/{}-{}-{}.json".format(save_location, ticker, m, y)):
                d = monthrange(y, m)[1]
                query = gn.search(
                    ticker, from_='{}-{}-01'.format(y, m), to_='{}-{}-{}'.format(y, m, d))
                save(query, ticker, m, y, save_location)


def save(query, ticker, month, year, save_location):
    with open("{}/{}-{}-{}.json".format(save_location, ticker, month, year), "w") as f:
        json.dump(query, f)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python {} <TICKER> <FROM_YEAR> <TO_YEAR> <SAVE_LOCATION>".format(
            sys.argv[0]))
        exit()

    ticker = sys.argv[1]
    from_year = int(sys.argv[2])
    to_year = int(sys.argv[3])
    save_location = sys.argv[4]
    scrape(ticker, from_year, to_year, save_location)
