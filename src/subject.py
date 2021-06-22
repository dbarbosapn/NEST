import NEAT


class Subject:

    def __init__(self, genome, config, base_budget, fee):
        self.genome = genome
        self.net = NEAT.create_net(genome, config)
        self.base_budget = base_budget
        self.budget = base_budget
        self.fee = fee
        self.total_pos = 0
        self.total_pos_price = 0
        self.total_sold = 0
        self.operations = []
        self.total_spent = 0
        self.update_fitness(0)

    def update_fitness(self, price):
        self.genome.fitness = self.get_realized_profit()

    def get_realized_profit(self):
        return self.total_sold - self.total_spent

    def get_profits(self, price):
        return self.total_sold, self.total_pos * (price - self.total_pos_price)

    def evaluate(self, data, price):
        # Also add as input: Current Price | Profit/Loss in position (pct) | Position Size | Budget (pct on base)
        # Total Inputs: 250
        if self.total_pos > 0:
            pl_pos = (price - self.total_pos_price) / self.total_pos_price
        else:
            pl_pos = 0

        pct_budget = self.budget / self.base_budget

        inputs = [price, pl_pos, self.total_pos, pct_budget]
        inputs.extend(data)

        return self.net.activate(inputs)

    def buy(self, percent, price, day):
        value = percent * self.budget
        if value > 0.1:
            new_pos = value / price
            p_sum = self.total_pos * self.total_pos_price
            p_sum += new_pos * price
            self.total_pos += new_pos
            self.total_pos_price = p_sum / self.total_pos
            self.budget -= value
            self.operations.append(["BUY", new_pos, price, day])
            self.update_fitness(price)
            self.total_spent += value + (self.fee * value)

    def sell(self, percent, price, day):
        sell_pos = percent * self.total_pos
        if sell_pos > 0.1:
            self.total_pos -= sell_pos
            self.operations.append(["SELL", sell_pos, price, day])
            self.total_sold += sell_pos * price
            self.update_fitness(price)

    def notify_budget_cycle(self):
        self.budget += self.base_budget
