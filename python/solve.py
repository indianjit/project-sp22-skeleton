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

import cProfile
import pstats

from instance import Instance
from solution import Solution
from file_wrappers import StdinFileWrapper, StdoutFileWrapper


def solve_naive(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=instance.cities,
    )

def solveIt(instance: Instance) -> Solution:
    # profile = cProfile.Profile()
    # profile.enable()

    # for each pixel, have how many cities would be covered if a tower was placed there
    # go through each of the points and if placing a tower there would cover at least 1 city, consider it
    # when iterating, if a better option is found, only pick it with some probability 
    # which is dependent on the integral of the heightMap

    # once a point is picked, update the height map 3 * r around where tower is placed
    # figure out all places where a tower can be moved to and still cover all of its cities
    # if in any of these places, the penalty is less. Move there

    # remove any towers which uniquely cover no cities.
    maxCords = instance.D - 1
    storedPoints = []
    for y in range(0, maxCords + 1):
        for x in range(0, maxCords + 1):
            storedPoints.append(Point(x, y))
    

    storedCalc = dict()
    def pointsInRadius(centerPoint: Point, radius: int):
        dictVal = storedCalc.get((centerPoint, radius))
        if dictVal != None:
            # we already seen this point
            return dictVal
        cx = centerPoint.x
        cy = centerPoint.y
        validPoints = set()
        for x in range(max(cx - radius, 0), min(cx + radius, maxCords) + 1):
            for y in range(max(cy - radius, 0), min(cy + radius, maxCords) + 1):
                point = storedPoints[x + y * (maxCords+1)]
                if centerPoint.distance_obj(point) <= radius:
                    validPoints.add(point)
        
        storedCalc[(centerPoint, radius)] = validPoints
        return validPoints

    r = instance.coverage_radius
    p = instance.penalty_radius
    allCityPoints = set(instance.cities)
    towerPoints = set()
    
    cityTowers = dict() # {city: [tower1, tower2...], ...}
    heightMap = dict()
    penaltyMap = dict()
    allPoints = pointsInRadius(Point(0,0), 2*maxCords + 10)
    # initializing the dictionaries
    for point in allCityPoints:
        cityTowers[point] = []
    for point in allPoints:
        heightMap[point] = 0
        penaltyMap[point] = 0


    def isCity(point: Point):
        # return weather a point is a cityPoint
        return point in allCityPoints

    def isTower(point: Point):
        # returns weather a point is a towerPoint 
        return (point in towerPoints)

    def isUniqueCity(city):
        if city not in allCityPoints:
            raise Exception("point is not a city")
        
        if len(cityTowers[city]) <= 1:
            return True
        else:
            return False

    def getMyCities(tower):
        if tower not in towerPoints:
            raise Exception("no tower located at that point")

        myCities = set()

        for point in pointsInRadius(tower, r):
            if isCity(point) and isUniqueCity(point):
                myCities.add(point)
        return myCities
        
    def updateHeightMap(cities: list[Point], adding: bool):
        for cityPoint in cities:
            if isCity(cityPoint):
                pass
            else:
                raise Exception("non city point passed into updateHeightMap")
        
        if adding:
            updateVal = 1
        else:
            updateVal = -1

        for city in cities:
            for point in pointsInRadius(city, r):              
                heightMap[point] = heightMap[point] + updateVal

    updateHeightMap(list(allCityPoints), True)
    initHeightMap = heightMap.copy()



    def updatePenaltyMap(towerPoint: Point, adding: bool):
        if isTower(towerPoint):
            pass
        else:
            raise Exception("non tower point passed into updatePenaltyMap")
    
        if adding:
            updateVal = 1
        else:
            updateVal = -1

        for point in pointsInRadius(towerPoint, p):
            penaltyMap[point] = penaltyMap[point] + updateVal
            
    def chooseTowerPlacement():
        pool = []
        for point in allPoints:
            i = heightMap[point]
            i = i ** 2
            while i > 0:
                pool.append(point)
                i -= 1
        chosenPoint = random.choice(pool)
        j = 100

        while chosenPoint in towerPoints and j > 0:
            chosenPoint = random.choice(pool)
            j -= 1

        return chosenPoint

    def chooseTowerProb():
        prob = (1/(maxCords ** 2)) * 5000  
        for point in allPoints:
            if heightMap[point] >= 1:
                chosenPoint = point
                break
        for point in allPoints:
            if heightMap[point] >= heightMap[chosenPoint]:
                if random.randint(0, 100) < prob:
                    chosenPoint = point
        return chosenPoint



    def updateCityTowers(towerPoint: Point, adding: bool):
        for point in pointsInRadius(towerPoint, r):
            if isCity(point):
                cityTowerz = cityTowers[point]
                if adding:
                    cityTowerz.append(point)
                else:
                    if point not in cityTowerz:
                        raise Exception("tower was not connected to city which it is being removed from")
                    cityTowerz.remove(point)

    def getUncoveredCities():
        uncoveredCities = set()
        for city in allCityPoints:
            if len(cityTowers[city]) <= 0:
                uncoveredCities.add(city)
        return uncoveredCities



    def addTower(towerPoint: Point):
        if towerPoint in towerPoints:
            #raise Exception("attempting to place tower at a place where there is already a tower")
            print("already tower here not gonna do anything")
            return 
        
        towerPoints.add(towerPoint)
        updateHeightMap(list(getMyCities(towerPoint)), False)
        updatePenaltyMap(towerPoint, True)
        updateCityTowers(towerPoint, True)

        
    def removeTower(point):
        if point in towerPoints:
            pass
        else:
            raise Exception("attempting to remove tower where there is no tower")
        if len(getMyCities(point)) >= 1:
            raise Exception("removing tower will leave some cities uncovered")


        updatePenaltyMap(point, False)
        towerPoints.remove(point)
        updateCityTowers(point, False)

    def moveTower(startingPoint, endingPoint):
        if startingPoint not in towerPoints:
            raise Exception("no tower at starting point")
        if endingPoint in towerPoints:
            #raise Exception("locating to a place with a tower already there")
            print("tower already there.. not gonna do anything")
            return

        addTower(endingPoint)
        removeTower(startingPoint)

    def getWigglePoints(towerPoint):
        circles = []
        myCities = getMyCities(towerPoint)
        if len(myCities) == 0:
            return set()
        for city in myCities:
            circles.append(pointsInRadius(city, r))
        
        if len(circles) == 0:
            raise Exception("circles should have something in it")
        
        a = circles[0]
        for circle in circles:
            a = set.intersection(a, circle)
    
        wigglePoints = a
        if len(wigglePoints) <= 0:
            raise Exception("somehow no wiggle points?!?!")

        
        return wigglePoints
    
    def wiggle(towerPoint):
        if towerPoint not in towerPoints:
            raise Exception("not tower, cant wiggle")
        bestPenalty = penaltyMap[towerPoint]
        bestPoint = towerPoint

        wigglePoints = getWigglePoints(towerPoint)

        if len(wigglePoints) == 0:
            return

        for wigglePoint in wigglePoints:
            wigglePenalty = penaltyMap[wigglePoint]
            if wigglePenalty < bestPenalty or (initHeightMap[wigglePoint] > initHeightMap[bestPoint] and wigglePenalty == bestPenalty):
                bestPenalty = wigglePenalty
                bestPoint = wigglePoint
        
        if bestPoint != towerPoint:
            moveTower(towerPoint, bestPoint)
    
    while len(getUncoveredCities()) > 0:
        towerPlacement = chooseTowerPlacement()
        addTower(towerPlacement)

    maxIterations = 100
    i = maxIterations
    while i > 0:
        profile = cProfile.Profile()
        profile.enable()


        prevTowerPoints = towerPoints.copy()
        
        for tower in towerPoints:
            wiggle(tower)
        
        for tower in towerPoints.copy():
            if len(getMyCities(tower)) == 0:
                removeTower(tower)

        if prevTowerPoints == towerPoints:
            break
        i -= 1



    answer = Solution(
        instance=instance,
        towers=list(towerPoints),
    )

    # profile.disable()
    # ps = pstats.Stats(profile)
    # ps.sort_stats('cumtime') 
    # ps.print_stats()


    return answer

def solveItIter(instance: Instance, iters, target) -> Solution:
    # remove line below for future
    # number 4
    # my curr score : 1933
    i = iters
    bestSol = solveIt(instance)
    bestPenalty = bestSol.penalty() 
    print("init: ", bestPenalty)
    print("target: ", target)

    while i > 0 and bestPenalty > target:
        currSol = solveIt(instance)
        currPenalty = currSol.penalty()
        if currPenalty < bestPenalty:
            bestPenalty = currPenalty
            bestSol = currSol
        i -= 1

    return bestSol


SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive,
    "solveIt": solveIt,
    "solveItIter": solveItIter
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
