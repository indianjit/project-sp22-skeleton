"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""

import argparse
import math
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

def greedy(instance: Instance) -> Solution:
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


SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive,
    "greedy": greedy
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
