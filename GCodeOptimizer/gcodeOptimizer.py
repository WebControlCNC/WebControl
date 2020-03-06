from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import re
import math
import numpy as np
import random
import operator
import pandas as pd

# The idea for this class is to minimize the distance of G0 moves (i.e., moves above z-axis of 0.0)
# GCode optimization is not a straight travelling salesperson problem (TSP) because their are distinct start and stop
# coordinates involved.  In a TSP problem, optimizers just minimize the total travel time between discrete locations
# (i.e., cities).  This method would work well if all gcode was drill operations.  However, because each line has a
# start and stop, it doesn't apply.  This is more of a Taxi Cab Problem (TCP) where a taxi driver has a list
# of pickups and dropoffs and wants to optimize his route to minimize the travel time.  Whearas in the TSP, the
# "pickup" and 'dropoff" location is the same, in the TCP, they are different.
#
# The problems associated with optimizing gcode are:
#   1. Use of relative positioning will be challenging.  Solution might be to disallow in optimization
#   2.

# https://github.com/ezstoltz/genetic-algorithm/blob/master/genetic_algorithm_TSP.ipynb

class Path:
    x0 = 0 # beginning x,y of the gcode group
    y0 = 0
    x1 = 0 # end x,y of the gcode group
    y1 = 0
    startLine = 0 # index of first gcode line of gcode group in gcode file
    finishLine = 0 # index of last gcode line of gcode group in gcode file

    def __init__(self, x0, y0, x1, y1, startLine, finishLine):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.startLine = startLine
        self.finishLine = finishLine

    def distance(self, path):
        xDis = abs(self.x1 - path.x0)
        yDis = abs(self.y1 - path.y0)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance

    def __repr__(self):
        return "[("+str(self.x0)+","+str(self.y0)+")-("+str(self.x1)+","+str(self.y1)+") ("+str(self.startLine)+":"+str(self.finishLine)+")]"

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness = 0.0

    def routeDistance(self):
        if self.distance == 0:
            pathDistance = 0
            for i in range(0, len(self.route)):
                fromPath = self.route[i]
                toPath = None
                if i + 1 < len(self.route):
                    toPath = self.route[i + 1]
                else:
                    toPath = self.route[0]
                pathDistance += fromPath.distance(toPath)
            self.distance = pathDistance
        return self.distance

    def routeFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.routeDistance())
        return self.fitness

def createRoute(pathList):
    route = random.sample(pathList, len(pathList))
    return route


def initialPopulation(popSize, pathList):
    population = []

    for i in range(0, popSize):
        population.append(createRoute(pathList))
    return population

def rankRoutes(population):
    fitnessResults = {}
    for i in range(0,len(population)):
        fitnessResults[i] = Fitness(population[i]).routeFitness()
    return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)


def selection(popRanked, eliteSize):
    selectionResults = []
    df = pd.DataFrame(np.array(popRanked), columns=["Index", "Fitness"])
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100 * df.cum_sum / df.Fitness.sum()

    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100 * random.random()
        for i in range(0, len(popRanked)):
            if pick <= df.iat[i, 3]:
                selectionResults.append(popRanked[i][0])
                break
    return selectionResults


def matingPool(population, selectionResults):
    matingpool = []
    for i in range(0, len(selectionResults)):
        index = selectionResults[i]
        matingpool.append(population[index])
    return matingpool


def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []

    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))

    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    for i in range(startGene, endGene):
        childP1.append(parent1[i])

    childP2 = [item for item in parent2 if item not in childP1]

    child = childP1 + childP2
    return child


def breedPopulation(matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))

    for i in range(0, eliteSize):
        children.append(matingpool[i])

    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool) - i - 1])
        children.append(child)
    return children


def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if (random.random() < mutationRate):
            swapWith = int(random.random() * len(individual))

            city1 = individual[swapped]
            city2 = individual[swapWith]

            individual[swapped] = city2
            individual[swapWith] = city1
    return individual


def mutatePopulation(population, mutationRate):
    mutatedPop = []

    for ind in range(0, len(population)):
        mutatedInd = mutate(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop

def nextGeneration(currentGen, eliteSize, mutationRate):
    popRanked = rankRoutes(currentGen)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(matingpool, eliteSize)
    nextGeneration = mutatePopulation(children, mutationRate)
    return nextGeneration


def geneticAlgorithm(population, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(popSize, population)
    print("Initial distance: " + str(1 / rankRoutes(pop)[0][1]))

    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)

    print("Final distance: " + str(1 / rankRoutes(pop)[0][1]))
    bestRouteIndex = rankRoutes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]
    return bestRoute

def getXYFromGCode(gCodeLine, xTarget, yTarget):
    gCodeLine = gCodeLine.upper() + " "
    x = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
    if x:
        xTarget = float(x.groups()[0])
    y = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
    if y:
        yTarget = float(y.groups()[0])

    return xTarget, yTarget

def getZFromGCode(gCodeLine):
    gCodeLine = gCodeLine.upper() + " "
    zTarget = None
    z = re.search("Z(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
    if z:
        zTarget = float(z.groups()[0])
    return zTarget


class GCodeOptimizer(MakesmithInitFuncs):

    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass

    def optimize(self):
        pathList = []
        inPath = False
        index = 0
        startLine = 0
        currentX = None
        currentY = None
        maxZTarget = 0
        inHeader = True
        headerEnd = 0
        footerStart = 0
        #path list will hold the parsed gcode groups between G0 moves.
        for line in self.data.gcode:
            line = (line + " " )
            gString = line[line.find("G"): line.find("G") + 3]
            # print(str(currentX)+", "+str(currentY))
            #print(line)
            if gString == "G00" or gString == "G0 ": #found G0/G00
                if not inPath:
                    if currentX is None and currentY is None:
                        startX, startY = getXYFromGCode(line, currentX, currentY)
                        if startX == currentX and startY == currentY:
                            zTarget = getZFromGCode(line)
                            if float(zTarget) > float(maxZTarget):
                                maxZTarget = zTarget
                        else:
                            currentX = startX
                            currentY = startY
                            inHeader = False
                    else:
                        startX = currentX
                        startY = currentY
                        endX, endY = getXYFromGCode(line, currentX, currentY)
                        if endX == currentX and endY == currentY:
                            zTarget = getZFromGCode(line)
                            if float(zTarget) > float(maxZTarget):
                                maxZTarget = zTarget
                        currentX = endX
                        currentY = endY
                        inHeader = False
                else:
                    endX = currentX
                    endY = currentY
                    #print(str(startX) + ", " + str(startY)+" - "+str(endX) + ", " + str(endY))
                    pathList.append(Path(x0=float(startX),y0=float(startY),x1=float(endX),y1=float(endY),startLine=startLine, finishLine=index))
                    currentX, currentY = getXYFromGCode(line, currentX, currentY)
                    inPath = False

            elif gString == "G01" or gString == "G1 " or gString == "G02" or gString == "G2 " or gString == "G03" or gString == "G3 ": #found G1/G01/G2/G02/G3/G03
                endX, endY = getXYFromGCode(line, currentX, currentY)
                if endX == None and endY == None:
                    zTarget = getZFromGCode(line)
                    if float(zTarget) > float(maxZTarget):
                        maxZTarget = zTarget
                    else:
                        inHeader = False
                else:
                    if not inPath:
                        startLine = index
                        startX = currentX
                        startY = currentY
                    if not endX:
                        endX = startX
                    if not endY:
                        endY = startY
                    currentX = endX
                    currentY = endY
                    inPath = True
                    inHeader = False
            else:
                if inHeader:
                    headerEnd = index
            index = index + 1

        #for i in range(0, 25):
        #    pathList.append(Path(x0=int(random.random() * 200), y0=int(random.random() * 200), x1=int(random.random() * 200), y1=int(random.random() * 200) ) )
        #print(headerEnd)
        for path in pathList:
            print(path)

        bestRoute = geneticAlgorithm(population=pathList, popSize=100, eliteSize=20, mutationRate=0.01, generations=500)
        #for path in bestRoute:
        #    print(path)

        newGCode = []
        for i in range(0,headerEnd+1):
            #print(self.data.gcode[i])
            newGCode.append(self.data.gcode[i])

        for path in bestRoute:
            newGCode.append("G0 Z" + str(maxZTarget))
            newGCode.append("G0 X" + str(path.x0) + " Y" + str(path.y0))
            #print("G0 Z" + str(maxZTarget))
            #print("G0 X" + str(path.x0) + " Y" + str(path.y0))
            for i in range(path.startLine, path.finishLine ):
                newGCode.append(self.data.gcode[i])
                #print(self.data.gcode[i])

        finalGCode = ""
        for i in newGCode:
            finalGCode = finalGCode + i + "\n"
        self.data.actions.updateGCode(finalGCode)
        return True





