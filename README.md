# Effectively Coping With NP-Completeness

For the Fall 2020 offering of [CS 170](https://cs170.org/), we were tasked with solving and approximation solutions to an NP-complete problem. You can view the  project spec [here](https://i.imgur.com/2wGY68z.png) as well as in `project_sec.pdf`. We chose to formulate this problem as an [integer linear program](https://www.wikiwand.com/en/Integer_programming)

## Requirements
- Python 3.6+
- [NetworkX](https://networkx.github.io/documentation/stable/install.html)
- [Gurobi](https://www.gurobi.com/documentation/quickstart.html) or [CBC](https://projects.coin-or.org/Cbc)

Note that if you are using Gurobi, you will need to acquire an academic license.

## Files
- `parse.py`: functions to read/write inputs and outputs
- `solver.py`: code to solve inputs using CDC
- `solverg.py`: code to solve inputs using Gurobi (significantly faster runtime)
- `utils.py`: contains functions to compute cost and validate NetworkX graphs

## How to Run
- create a folder in the file tree where you want outputs to go
- change line 157 in `solverg.py` to the name of the created folder
- `python3 solverg.py foldername` will run the solver on a folder of inputs

We placed in the **top 10%** of our class of over 800 students. You can view the leaderboard [here](https://berkeley-cs170.github.io/project-leaderboard-fa20/) and our team's scores [here](https://berkeley-cs170.github.io/project-leaderboard-fa20/?team=WHOSE_TOES_ARE_THOSE).
