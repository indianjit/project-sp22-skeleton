"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""

import argparse
import math
import random
from mimetypes import init
from turtle import update
from point import Point
from pathlib import Path
from typing import Callable, Dict

from instance import Instance
from solution import Solution
from file_wrappers import StdinFileWrapper, StdoutFileWrapper


def solve_naive(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=instance.cities,
    )



def greedyFailed(instance: Instance) -> Solution:
    r = instance.coverage_radius
    maxCord = instance.D - 1
    uncovered = set(instance.cities)
    towerLocations = []
    heightMap = dict()
    def numUncoveredCitiesInServiceRadius(centerx, centery):
            answer = 0
            for x in range(max(0, centerx - r), min(maxCord, centerx + r)):
                for y in range(max(0, centery - r), min(maxCord, centery + r)):
                    potentialTowerCityDist = math.sqrt((x - centerx)**2 + (centery - y)**2)
                    # creating a new point below, might not register as a point in the set uncovered even if there cause new object
                    if potentialTowerCityDist <= r and Point(x, y) in uncovered:
                        answer += 1
            return answer
    def updateHeightMap(minX, maxX, minY, maxY):
            for x in range(minX, maxX + 1):
                for y in range(minY, maxY + 1):
                    heightMap[(x,y)] = numUncoveredCitiesInServiceRadius(x, y)
    def helper(key):
            return heightMap[key]
    def removeCitiesFromUncovered(towerx, towery):
            for x in range(max(0, towerx - r), min(maxCord, towerx + r)):
                for y in range(max(0, towery - r), min(maxCord, towery + r)):
                    potentialTowerCityDist = math.sqrt((x - towerx)**2 + (towery - y)**2)
                    # creating a new point below, might not register as a point in the set uncovered even if there cause new object
                    if potentialTowerCityDist <= r and Point(x, y) in uncovered:
                        # these are all uncovered cities with in service radius of tower
                        uncovered.discard(Point(x,y))
    while len(uncovered) > 0 :
        # intializes the height map
        updateHeightMap(0, maxCord, 0, maxCord)
        # find the heighest point in the height map
        heighestPoint = max(heightMap.keys(), key = helper)
        towerLocations.append(Point(heighestPoint[0], heighestPoint[1]))
        print(heightMap[(heighestPoint[0], heighestPoint[1])])
        print(len(uncovered))
        removeCitiesFromUncovered(heighestPoint[0], heighestPoint[1])
    return Solution(
        instance = instance,
        towers = towerLocations,
    )



def toTuples(thingy):
    tups = []
    for point in thingy:
        tups.append((point.x, point.y))
    return tups

def toPoints(tups):
    points = []
    for tup in tups:
        points.append(Point(tup[0], tup[1]))
    return points


def greedy(instance: Instance) -> Solution:
    r = instance.coverage_radius
    maxCord = instance.D - 1
    uncovered = set(instance.cities)
    towerLocations = []
    heightMap = dict()

    def updateHeightMap():
        for x in range(0, maxCord + 1):
            for y in range(0, maxCord + 1):
                heightMap[Point(x,y)] = 0
        for city in uncovered:
            for x in range(max(0, city.x - r), min(maxCord, city.x + r) + 1):
                for y in range(max(0, city.y - r), min(maxCord, city.y + r) + 1):
                    dist = math.sqrt((x - city.x)**2 + (city.y - y)**2)
                    if dist <= r:
                        heightMap[Point(x,y)] += 1                
    def findHeightestPoint():
        def helper(key):
                return heightMap[key]
        return max(heightMap.keys(), key = helper)
    def removeCitiesFromUncovered(towerPoint):
        towerx = towerPoint.x
        towery = towerPoint.y
        for x in range(max(0, towerx - r), min(maxCord, towerx + r) + 1):
            for y in range(max(0, towery - r), min(maxCord, towery + r) + 1):
                potentialTowerCityDist = math.sqrt((x - towerx)**2 + (towery - y)**2)
                if potentialTowerCityDist <= r and Point(x, y) in uncovered:
                    # these are all uncovered cities with in service radius of tower
                    uncovered.remove(Point(x,y))
    while len(uncovered) > 0 :
        updateHeightMap()
        heighestPoint = findHeightestPoint()
        towerLocations.append(heighestPoint)
        highVal = heightMap[heighestPoint]
        removeCitiesFromUncovered(heighestPoint)
    
    return Solution(
        instance = instance,
        towers = towerLocations,
    )



def greedyConsiderate(instance: Instance) -> Solution:
    r = instance.coverage_radius
    p = instance.penalty_radius
    maxCord = instance.D - 1
    uncovered = set(instance.cities)
    towerPoints = []
    heightMap = dict()
    penaltyMap = dict()
    

    def iterateHelper(minX, maxX, minY, maxY):
        # returns all the points within the range
        possiblePoints = set()
        for x in range(max(0, minX), min(maxCord, maxX) + 1):
            for y in range(max(0, minY), min(maxCord, maxY) + 1):
                possiblePoints.add(Point(x, y))
        return possiblePoints

    allPoints = iterateHelper(0, maxCord, 0, maxCord)

    def updateHeightMap():
        for point in allPoints:
            heightMap[point] = 0
        for city in uncovered:
            possiblePoints = iterateHelper(city.x - r, city.x + r, city.y - r, city.y + r)
            for point in possiblePoints:
                dist = math.sqrt((point.x - city.x)**2 + (city.y - point.y)**2)
                if dist <= r:
                    heightMap[point] += 1

    def updatePenaltyMap():
        for point in allPoints:
            penaltyMap[point] = 0 
        for tower in towerPoints:
            penaltyPoints = iterateHelper(tower.x - p, tower.x + p, tower.y - p, tower.y + p)
            for point in penaltyPoints:
                penaltyMap[point] += 1
    
    def choosePoint():
        mostCitiesInRadius = max(heightMap.values())
        maxPoints = []
        for point in allPoints:
            if heightMap[point] >= mostCitiesInRadius:
                maxPoints.append(point)
        def helper(point):
            return penaltyMap[point]
        return min(maxPoints, key = helper)
    def removeCitiesFromUncovered(towerPoint):
        towerx = towerPoint.x
        towery = towerPoint.y
        pointsInRange = iterateHelper(towerx - r, towerx + r, towery - r, towery + r)
        for point in pointsInRange:
            dist = math.sqrt((point.x - towerx)**2 + (point.y - towery)**2)
            if dist <= r and point in uncovered:
                # these are all uncovered cities with in service radius of tower
                uncovered.remove(point)
    
    while len(uncovered) > 0:
        updateHeightMap()
        updatePenaltyMap()
        chosenPoint = choosePoint()
        towerPoints.append(chosenPoint)
        highVal = heightMap[chosenPoint]
        removeCitiesFromUncovered(chosenPoint)
    
    return Solution(
        instance = instance,
        towers = towerPoints,
    )



def generateSol(instance: Instance) -> Solution:
    r = instance.coverage_radius
    maxCord = instance.D - 1
    uncovered = set(instance.cities)
    towerPoints = set()
    heightMap = dict()

    def iterateHelper(minX, maxX, minY, maxY):
        # returns all the points within the range
        possiblePoints = set()
        for x in range(max(0, minX), min(maxCord, maxX) + 1):
            for y in range(max(0, minY), min(maxCord, maxY) + 1):
                possiblePoints.add(Point(x, y))
        return possiblePoints
    allPoints = iterateHelper(0, maxCord, 0, maxCord)
    
    def pointsInRadius(centerPoint, radius):
        maybeValidPoints = iterateHelper(centerPoint.x - radius, centerPoint.x + radius, centerPoint.y - radius, centerPoint.y + radius)
        validPoints = []
        for point in maybeValidPoints:
            dist = math.sqrt((point.x - centerPoint.x)**2 + (point.y - centerPoint.y)**2) 
            if dist <= radius:
                validPoints.append(point)
        return validPoints

    def updateHeightMap():
        for point in allPoints:
            heightMap[point] = 0
        for city in uncovered:
            for point in pointsInRadius(city, r):
                heightMap[point] += 1
                

    def allValidPlacements():
        # returns a set of all points which if a tower was placed there,
        # that tower would have at least one city within its service area
        validPoints = set()
        for point in allPoints:
            if heightMap[point] >= 1:
                validPoints.add(point)
        return validPoints

    def removeCitiesFromUncovered(towerPoint):
        for point in pointsInRadius(towerPoint, r):
            if point in uncovered:
                uncovered.remove(point)
    

    def addTower(towerPoint):
        towerPoints.add(towerPoint)
        removeCitiesFromUncovered(towerPoint)
        

    while len(uncovered) > 0:
        updateHeightMap()
        chosenPoint = random.choice(list(allValidPlacements()))
        addTower(chosenPoint)
    
    return Solution(
        instance = instance,
        towers = list(towerPoints),
    )



def iterateOnTowers(instance: Instance, solutionGenFunc) -> Solution:
    r = instance.coverage_radius
    p = instance.penalty_radius
    maxCord = instance.D - 1
    allCityPoints = set(instance.cities)
    uncovered = set(instance.cities)
    heightMap = dict()
    penaltyMap = dict()
    coverageMap = dict() # {CityPoint: numTowersFromWhichCityGetsPower}
    initHeightMap = dict()
    
    def iterateHelper(minX, maxX, minY, maxY):
        # returns all the points within the range
        possiblePoints = set()
        for x in range(max(0, minX), min(maxCord, maxX) + 1):
            for y in range(max(0, minY), min(maxCord, maxY) + 1):
                possiblePoints.add(Point(x, y))
        return possiblePoints

    def pointsInRadius(centerPoint, radius):
        maybeValidPoints = iterateHelper(centerPoint.x - radius, centerPoint.x + radius, centerPoint.y - radius, centerPoint.y + radius)
        validPoints = []
        for point in maybeValidPoints:
            dist = math.sqrt((point.x - centerPoint.x)**2 + (point.y - centerPoint.y)**2) 
            if dist <= radius:
                validPoints.append(point)
        return validPoints
    allPoints = iterateHelper(0, maxCord, 0, maxCord)

    
    def myCities(towerPoint):
        # given a towerPoint will return a list of cityPoints which recieve power from only that tower
        myCityPoints = []
        for point in pointsInRadius(towerPoint, r):
            if point in allCityPoints and coverageMap[point] <= 1:
                myCityPoints.append(point)
        return myCityPoints
        
    def myRivals(towerPoint):
        # given a towerPoint will return all towerPoints which are within penalty radius of towerPoint
        myRivalPoints = []
        for point in pointsInRadius(towerPoint, p):
            if point in towerPoints:
                myRivalPoints.append(point)
        return myRivalPoints

    def updateCoverageMap():
        for point in allPoints:
            coverageMap[point] = None
        for city in allCityPoints:
            coverageMap[city] = 0
        for city in allCityPoints:
            for point in pointsInRadius(city, r):
                if point in towerPoints:
                    coverageMap[city] += 1

    def updateHeightMap():
        for point in allPoints:
            heightMap[point] = 0
        for city in uncovered:
            for point in pointsInRadius(city, r):
                heightMap[point] += 1

    def updatePenaltyMap():
        for point in allPoints:
            penaltyMap[point] = 0 
        for towerPoint in towerPoints:
            for point in pointsInRadius(towerPoint, p):
                penaltyMap[point] += 1
    
    def getWigglePoints(towerPoint):
        # given a towerPoint will return a list of all of the points which the tower can be moved to while 
        # leaving all of the cities still covered.
        myResponsibilities = myCities(towerPoint)
        wigglePoints = [towerPoint]
        def isValid(wigglePoint):
            uncoveredResponsibilities = myResponsibilities.copy()
            for point in pointsInRadius(wigglePoint, r):
                if point in uncoveredResponsibilities:
                    # meaning the point is a city
                    uncoveredResponsibilities.remove(point)
            if len(uncoveredResponsibilities) == 0:
                return True
            else:
                return False

        possibleWigglePoints = pointsInRadius(towerPoint, 2 * r)
        for point in possibleWigglePoints:
            if isValid(point):
                wigglePoints.append(point)
        return wigglePoints

    def wiggleTowers():
        newTowerPoints = set()
        for towerPoint in towerPoints:
            wigglePoints = getWigglePoints(towerPoint)
            # wiggle points has len 0 if the solution would still be valid of tower was removed
            numBestRivals = len(myRivals(towerPoint))
            bestPoint = towerPoint
            for wigglePoint in wigglePoints:
                numNewRivals = len(myRivals(wigglePoint))
                if numNewRivals < numBestRivals:
                    # we found a betterPlace!
                    numBestRivals = numNewRivals
                    bestPoint = wigglePoint
            newTowerPoints.add(bestPoint)
        return newTowerPoints

    updateHeightMap()
    initHeightMap = heightMap.copy()

    towerPoints = solutionGenFunc(instance).towers

    sol = Solution( instance = instance, towers = list(towerPoints))
    if not sol.valid():
        print(toTuples(towerPoints))

    i = 0
    numIterations = 10

    while i < numIterations:
        updateCoverageMap()
        updatePenaltyMap()
        prevTowerPoints = towerPoints.copy() 
        towerPoints = wiggleTowers()
        print("itering", i)

        # gets rid of un needed points

        for tower in towerPoints.copy():
            if len(myCities(tower)) == 0:
                print("removed")
                towerPoints.remove(tower)
                updateCoverageMap()
        updatePenaltyMap()
        
        if prevTowerPoints == towerPoints:
            break
        i += 1

    return Solution(
        instance = instance,
        towers = list(towerPoints),
    )



def greedyIterative(instance: Instance) -> Solution:
    return iterateOnTowers(instance, greedyConsiderate)

def randIterative(instance: Instance) -> Solution:
    i = 0
    numIterations = 20
    bestSol = iterateOnTowers(instance, generateSol)
    bestPenalty = bestSol.penalty()
    while i < numIterations:
        print("on iteration", i)
        currSol = iterateOnTowers(instance, generateSol)
        currPenalty = currSol.penalty()
        print(currSol.valid())
        if (not bestSol.valid()) or (currPenalty < bestPenalty and currSol.valid()):
            print("foundNewBest")
            bestSol = currSol
            bestPenalty = currPenalty
        i += 1
    print("towers:", toTuples(bestSol.towers))
    print("citiess:", toTuples(bestSol.instance.cities))
    print(bestPenalty)
    return bestSol

def randBubble(instance: Instance) -> Solution:
    i = 0
    numIterations = 300
    bestSol = generateSol(instance)
    bestPenalty = bestSol.penalty()
    while i < numIterations:
        print("on iteration", i)
        currSol =  generateSol(instance)
        currPenalty = currSol.penalty()
        print(currSol.valid())
        if currPenalty < bestPenalty:
            bestSol = currSol
            bestPenalty = currPenalty
        i += 1
    print("towers:", toTuples(bestSol.towers))
    print("citiess:", toTuples(bestSol.instance.cities))
    print(bestPenalty)
    return bestSol



SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive,
    "greedy": greedy,
    "greedyConsiderate": greedyConsiderate,
    "greedyIterative": greedyIterative,
    "randIterative": randIterative,
    "randBubble": randBubble
}


# You shouldn't need to modify anything below this line.
def infile(args):
    if args.input == "-":
        return StdinFileWrapper()

    return Path(args.input).open("r")


def outfile(args):
    if args.output == "-":
        return StdoutFileWrapper()

    return Path(args.output).open("w")


def main(args):
    with infile(args) as f:
        instance = Instance.parse(f.readlines())
        solver = SOLVERS[args.solver]
        solution = solver(instance)
        assert solution.valid()
        with outfile(args) as g:
            print("# Penalty: ", solution.penalty(), file=g)
            solution.serialize(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a problem instance.")
    parser.add_argument("input", type=str, help="The input instance file to "
                        "read an instance from. Use - for stdin.")
    parser.add_argument("--solver", required=True, type=str,
                        help="The solver type.", choices=SOLVERS.keys())
    parser.add_argument("output", type=str,
                        help="The output file. Use - for stdout.",
                        default="-")
    main(parser.parse_args())
