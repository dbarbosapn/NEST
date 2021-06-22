# NEST (Neuro-Evolutionary Stock Trading)

What if there was a brain that would evolve itself to succeed at stock trading?

NEST is a project that aims to do that. By using the NEAT algorithm, we try to solve this problem.

## The Data

Each subject's neural network will contain 250 inputs and 1 output.

### The Inputs

The inputs are:

- The last 120 days of stock closing prices
- The last 120 days of stock volume
- The sentiment score of the news of the last 6 months
- Current stock price
- The current profit/loss of the open positions
- The size of the current position
- Budget

### The Output

The output is a tanh-activated value (-1 to 1). Its value is interpreted as the percentage of the budget to be spent on buying/selling stock, depending on if the value is positive or negative.

## The Subject

The subject is where the simulation happens. Each month, there is a budget to invest. If there is money left at the end of the month, it will be accumulated on the next one, increasing the budget size.

There are also fees when there is a purchase. This is to try to create a realistic simulation of a real life situation

## The Results

There are some really interesting results with this project. The subjects were able to get ~44% ROI on TSLA stock, from 2018 to 2020, with a 250$ monthly budget. Unfortunately, if we save the same subject, already trained, and make ito trade during a different period, it gets much worse results (usually negative).

From my perspective, it seems that the subjects are actually learning which are good/bad prices and not actually using the data properly.

How to fix this? Maybe the inputs should be different. Maybe it needs more training. Maybe it should be on a bigger time interval.
Be free to add comments on this one.
