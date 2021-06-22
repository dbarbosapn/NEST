import neat


def init():
    config = neat.config.Config(
        neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, "src/neat.cfg")

    pop = neat.Population(config)
    return pop


def create_net(genome, config):
    return neat.nn.recurrent.RecurrentNetwork.create(genome, config)
