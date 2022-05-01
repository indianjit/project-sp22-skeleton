"""Runs the solver on all instances.

Modify this file to run your solve on all input files.

To read all files from inputs and write to outputs, run
`python3 python/solve_all.py inputs outputs` in the root directory.
"""


import argparse
import enum
import multiprocessing
import os
from pathlib import Path
from threading import BoundedSemaphore

import requests

from instance import Instance
from solution import Solution

# Modify this line to import your own solvers.
# YOUR CODE HERE
from solve import solve_naive

from solve import solveIt
from solve import solveItIter


class Size(enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"




def solver(size: Size, instance: Instance, inf) -> Solution:
    # Modify this function to use your imported solvers.
    # YOUR CODE HERE
    #return solve_naive(instance)
    #return greedy(instance)
    #return greedyConsiderate(instance)
    #return greedyIterative(instance)
    useNaive = []
    myPenaltyList = []

    def getTarget():        
        # target is to get in the top 6 at least!
        if size == Size.SMALL:
            top = 3
            sizze  = "small"
        elif size == Size.MEDIUM:
            top = 6
            sizze  = "medium"
        elif size == Size.LARGE:
            top = 10
            sizze  = "large"

        size_number_in = str(inf).removeprefix("inputs\\")
        number_in = size_number_in.removeprefix(sizze  + "\\")
        number = number_in.removesuffix(".in")

        response = requests.get(f"https://project.cs170.dev/scoreboard/{sizze}/{number}")
        dictionary = response.json()
        teamScores = []
        for entry in dictionary["Entries"]:
            if entry["TeamName"] == "greedyGoobers":
                myPenalty = entry["TeamScore"]
                myPenaltyList.append(myPenalty)
            teamScores.append(entry["TeamScore"])
        teamScores.sort()
        
        target = teamScores[top]
        if myPenalty < target:
            # the below line is so weird lol
            useNaive.append("True")
        return target
    
    target = getTarget() + 1

    if useNaive:
        return solve_naive(instance)


    # teamScores is now in ascending order
    if size == Size.SMALL:
        maxIters = 4000
    elif size == Size.MEDIUM:
        maxIters = 1000
    elif size == Size.LARGE:
        maxIters = 100
    
    sol = solveItIter(instance, maxIters, target)
    if sol.penalty() < myPenaltyList[0]:
        print(f"improvement of {sol.penalty() - myPenaltyList[0]}!")
        if sol.penalty() <= target:
            print(f"met target of {target} with init of {myPenaltyList[0]}")
    return sol


# You shouldn't need to modify anything below this line.
def removesuffix(s: str, suffix: str):
    if not s.endswith(suffix):
        return s

    return s[:-len(suffix)]


def traverse_files(inroot: str, outroot):
    for size in os.listdir(inroot):
        for inf in os.listdir(os.path.join(inroot, size)):
            if not inf.endswith(".in"):
                continue
            outf = f"{removesuffix(inf, '.in')}.out"
            yield (size, Path(inroot) / size / inf, Path(outroot) / size / outf)


def solve_one(args):
    size, inf, outf = args
    try:
        with open(inf) as f:
            instance = Instance.parse(f.readlines())
        assert instance.valid()


        solution = solver(Size(size), instance, inf)
        assert solution.valid()

        with outf.open('w') as f:
            solution.serialize(f)

    except Exception as e:
        print(f"{size} job failed ({inf}):", e)
    else:
        print(f"{str(inf)}: solution found with penalty", solution.penalty())


def main(args):
    outroot = Path(args.outputs)
    try:
        outroot.mkdir(exist_ok=False)
        (outroot / Size.SMALL.value).mkdir(exist_ok=False)
        (outroot / Size.MEDIUM.value).mkdir(exist_ok=False)
        (outroot / Size.LARGE.value).mkdir(exist_ok=False)
    except FileExistsError as e:
        print("===================== ERROR =====================")
        print("Output directory or subdirectory already exists!")
        print("Cowardly refusing to overwrite output files.")
        print("Move the output directory or write to a different folder.")
        print("===================== ERROR =====================")
        raise e

    with multiprocessing.Pool(args.parallelism) as pool:
        pool.map(solve_one, traverse_files(args.inputs, args.outputs))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs a solver over all inputs.")
    parser.add_argument("inputs", type=str,
                        help="Path to the inputs (read) folder.")
    parser.add_argument("outputs", type=str,
                        help="Path to the outputs (write) folder.")
    parser.add_argument("--parallelism", type=int,
                        help="Number of processes to spawn. Default: number of CPU cores.", default=None)
    args = parser.parse_args()

    if args.parallelism is None:
        args.parallelism = multiprocessing.cpu_count()
        print(f"Info: using parallelism=cpu_count() ({args.parallelism})")
    assert args.parallelism > 0, f"Can't use f{args.parallelism} cpus!"

    main(args)
