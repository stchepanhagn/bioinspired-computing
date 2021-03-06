"""game.py

This file stands for the main entry point
of the whole algorithm.
"""

#Teste

from genetic_programming import GeneticProgramming

if __name__ == "__main__":

    populationSize = 100
    maxGenerations = 100

    gp = GeneticProgramming(populationSize, maxGenerations)

    bestIndividual = gp.run()

    print "Return Individual"
    print "Fitness", bestIndividual.fitness
    print bestIndividual.printTree()

