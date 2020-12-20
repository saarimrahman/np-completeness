import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness
import sys
from os.path import basename, normpath
import glob
from collections import defaultdict
from queue import Queue
from pathlib import Path
from mip import Model, xsum, maximize, INTEGER, BINARY, OptimizationStatus, CBC, GRB 
import numpy as np
import math
import time

def solve(G, s):
    """
    Args:
        G: networkx.Graph
        s: stress_budget
    Returns:
        D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
        k: Number of breakout rooms
    """

    def getStress(s1, s2):
        return G.get_edge_data(s1, s2)['stress']

    def getHappiness(s1, s2):
        return G.get_edge_data(s1, s2)['happiness']

    def runSolver(k):
        # return dict, k
        m = Model(solver_name=GRB)
        
        #######################
        ###### Variables ######
        #######################

        """
        x[s1][r] = binary var if student s1 is in room r
        n x k matrix
        Room     0 1 2 3   Student
                [1 0 0 0]    0
                [1 1 0 1]    1
                [1 1 0 1]    2
        """
        x = [[m.add_var(name='x_{}_{}'.format(i, l), var_type='B') for l in range(k)] for i in range(n)]

        """
        y[r][s1][s2] = binary var if s1 and s2 are in room r
        Each entry of s is a sqaure n x n matrix
                [(0, 0) ... (i, 0)]
                [ ...   ...   ... ]
                [(j, 0) ... (i, j)]
        all entries below the diagonal are repeated. 
        """
        y = []
        for l in range(k):
            y.append([[m.add_var(name='y_{}_{}_{}'.format(i, j, l), var_type='B') for i in range(n)] for j in range(n)])

    
        #######################
        ##### Constraints #####
        #######################

        # https://cs.stackexchange.com/questions/12102/express-boolean-logic-operations-in-zero-one-integer-linear-programming-ilp?fbclid=IwAR0DTuP7zy4KUkgU_Vxip-21mMd0Gysw_EE1-BwGJtMz3BdPmDbTaAoPGI8
        for l in range(k):
            for i in range(n): 
                for j in range(i + 1, n):
                    m += x[i][l] + x[j][l] - 1 <= y[l][i][j]
                    m += x[i][l] >= y[l][i][j]
                    m += x[j][l] >= y[l][i][j]
        
        # ensures each student can only be in 1 room
        for i in range(n):
            m += xsum(x[i][l] for l in range(k)) == 1

        # ensures that rooms have at least 1 person
        for l in range(k):
            m += xsum(x[i][l] for i in range(n)) >= 1

        # ensures each room meets stress requirement
        for l in range(k):
            m += xsum(y[l][i][j] * getStress(i, j) for i in range(n) for j in range(i + 1, n)) <= S_MAX / k

        # optimize for happiness
        m.objective = maximize(xsum(y[l][i][j] * getHappiness(i, j) for l in range(k) for i in range(n) for j in range(i + 1, n)))

        solution = {}
        m.max_gap = 0.05
        status = m.optimize(max_seconds=300) # TRY 60
        if status == OptimizationStatus.OPTIMAL:
            print('optimal solution cost {} found'.format(m.objective_value))
        elif status == OptimizationStatus.FEASIBLE:
            print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
        elif status == OptimizationStatus.NO_SOLUTION_FOUND:
            print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
        elif status == OptimizationStatus.INFEASIBLE:
            print('infeasible: ')
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print('solution:')
            for v in m.vars:
                if abs(v.x) > 1e-6: # only printing non-zeros
                    print('{} : {}'.format(v.name, v.x))
                    student_room = v.name.split('_')
                    if student_room[0] == 'x':
                        solution[int(student_room[1])] = int(student_room[2])
            solution = dict(sorted(solution.items(), key=lambda item: item[1]))
        return solution

    n = G.number_of_nodes() # number of students
    S_MAX, K_LOWER, K_UPPER = s, 2, n - 1
    best_D, best_K, best_happiness = {}, K_LOWER, 0

    for k in range(K_LOWER, K_UPPER + 1):
        D = runSolver(k)
        if D:
            curr_happiness = calculate_happiness(D, G)
            if curr_happiness > best_happiness:
                best_D = D
                best_K = k
                best_happiness = curr_happiness
    print('BEST SOLUTION: {} rooms -'.format(best_K), best_D)
    return best_D, best_K

# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
#     assert len(sys.argv) == 2
#     path = sys.argv[1]
#     G, s = read_input_file(path)
#     D, k = solve(G, s)
#     assert is_valid_solution(D, G, s, k)
#     print("Total Happiness: {}".format(calculate_happiness(D, G)))
#     write_output_file(D, 'outputs/test.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# HOW TO RUN: 
    # KEV - python3 solverg.py large_1_80/
    # VIK - python3 solverg.py large_81_160/
    # SAAR - python3 solverg.py large_161_242/
if __name__ == '__main__':
    assert len(sys.argv) == 2
    path = sys.argv[1]
    inputs = glob.glob(path + '*')

    for input_path in inputs:
        # !!!!!
        # CREATE FOLDER IN FILE TREE AND 
        # CHANGE BELOW TO FOLDER NAME
        # KEV - gurobi_large_1_80_output/
        # VIK - gurobi_large_81_160_output/
        # SAAR - gurobi_large_161_242_output/
        FOLDER_NAME = 'outputs/'
        output_path =  FOLDER_NAME + basename(normpath(input_path))[:-3] + '.out'
        G, s = read_input_file(input_path)
        D, k = solve(G, s)
        assert is_valid_solution(D, G, s, k)
        happiness = calculate_happiness(D, G)
        write_output_file(D, output_path)
