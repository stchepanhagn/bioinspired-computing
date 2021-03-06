"""genetic_programming.py

This file stands for the genetic programming class
that is used to execute the algorithm itself. It
contains genetic operators (such as crossover and
mutation).
"""

import random
import genetic_operators as gop
from tree import Tree
from random import randint
import utils

class GeneticProgramming:

    def __init__(self,populationSize,maxGenerations,elitismPercentage=0.1,crossoverProbability=0.5,tournamentSize=5,mutationPercentage=0.05,mutationProbability=0.03):
        """
        "Constructor" of the class. Initializes the main components and parameters
        of the Genetic Program.

        :param populationSize:       population size of each generation.
        :param maxGenerations:       max number of generations in the execution.
        :param elitismPercentage:    percentage of the population that will be considered elite, which will be
                                     added directly to the next population. Default value is 0.1 (10%).
        :param crossoverProbability: probability of occurring crossover. Default value is 0.5 (50%).
        :param tournamentSize:       the size of the tournament, which is responsible for choosing the parents
                                     that will be used in the crossover. Default value is 5 (5 participants).
        :param mutationPercentage:   related to the percentage of the population that will be mutated in each
                                     generation. Default value is 0.05 (5%).
        :param mutationProbability:  probability of occurring mutation in a given individual. Default value is
                                     0.03 (3%).
        """
		
        # Funcoes
        self.functions = [n.value for n in utils.Node];

        # Terminais
        self.terminals = [n.value for n in utils.Moves];

        self.population = [];

        # Tamanho da populacao
        self.populationSize =  populationSize

        # Numero maximo de geracoes
        self.maxGenerations = maxGenerations;

        # Percentual de Elitismo
        self.elitismPercentage = elitismPercentage;

        # Probabilidade de Ocorrencia de  Croosover
        self.crossoverProbability = crossoverProbability;

        # Tamanho do torneio
        self.tournamentSize = tournamentSize;

               # Probabilidade de Ocorrencia de Mutacao 
        self.mutationPercentage = mutationPercentage;

               # Probabilidade de Mutacao dos nodos
        self.mutationProbability = mutationProbability;

    def generatePopulation(self, tree, left):
		# populate tree
        # left param is a boolean variable that
        # indicates whether the branch to be created is
        # left or right

        if left:
            tree.value = self.terminals[randint(0,len(self.terminals)-1)]
            return
        if randint(0,1) <  1:
            tree.value = self.terminals[randint(0,len(self.terminals)-1)]
            return

        tree.left = Tree()
        tree.right = Tree()
        
        tree.value = self.functions[randint(0,len(self.functions)-1)]

        self.generatePopulation(tree.left, 1)
        self.generatePopulation(tree.right, 0)

    def generateInitialPopulation(self):
        """
        Generates the initial population of the evolution
        """

        # iterate over populationSize creating a new tree
        # for each element
        for x in range(self.populationSize):
            new = Tree()
            new.left = Tree()
            new.right = Tree()
            new.value = self.functions[randint(0,2)]
            self.generatePopulation(new.left, 1)
            self.generatePopulation(new.right, 0)
            self.population.append(new)

            
    def getNextGeneration(self):
        """
        Generates Next Generation 
        
        - Executa Elitismo
        - Executa CrossOver
        - Executa Mutacoes
        
        """

        # elitism 
        # create the set that will be part of the next generation
        nextPopulation = gop.elitism(self.population, self.elitismPercentage)
        
        # get the size of the elite set
        eliteSize = len(nextPopulation)

        while (len(nextPopulation) < len(self.population)):

            if randint(0, 100) < (self.crossoverProbability * 100):
                parentTuple = gop.getParentByTournament(self.population, self.tournamentSize)
                children = gop.crossover(parentTuple[0], parentTuple[1], self.crossoverProbability)
                # add children to the next generation
                nextPopulation.append(children[0])
                nextPopulation.append(children[1])            
        
            if randint(0, 100) < (self.mutationProbability * 100):
                # 'aux' is the nastiest...! Please refrain from using these meaningless names!!!
                # computes a random index
                index = randint(0, len(self.population) - 1)
                individual = self.population[index]

                self.population.pop(self.population.index(individual))
                children = gop.mutation(individual, self.functions, self.terminals, self.mutationProbability)
            
                # add the mutated individual to the next generation set
                nextPopulation.append(children)

        return nextPopulation

    def run(self):
        """
        Executes the genetic program.
        :return: the best individual (solution) found to the problem.
        """

        numGenerations = 0;

		# best individual    
        best = Tree()

        self.generateInitialPopulation();
        
        while(numGenerations < self.maxGenerations):

            # calculate fitness to all individuals in population
            for current in self.population:
                current.fitness = utils.calculateFitness(current);

                # get the best fitness, which is the lowest one
                if current.fitness < best.fitness:
                    best = current;

            self.population = self.getNextGeneration();
            numGenerations += 1;

        return best;
