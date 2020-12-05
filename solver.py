import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_happiness
import sys
from os.path import basename, normpath
import glob
from collections import defaultdict
from mip import Model, xsum, maximize, INTEGER, BINARY, OptimizationStatus, CBC
import math
import pprint

def solve(G, s):
    """
    Args:
        G: networkx.Graph
        s: stress_budget
    Returns:
       
        D: Dictionary mapping for student to breakout room r e.g. {0:2, 1:0, 2:1, 3:2}
        k: Number of breakout rooms
    """

    S_MAX = s
    n = G.number_of_nodes() # number of students
    # s_ij is stress from i to j (given)
    # h_ij is happines from i to j (given)
    K_UPPER, K_LOWER = n // 2, 2
    k = 3

    
    edges = defaultdict(list) # edges -> dict mapping [(node, neighbor)] = [happiness, stress]

    
    for edge in G.edges():
        node, neighbor = edge[0], edge[1]
        happiness = G.edges[node, neighbor]['happiness']
        stress = G.edges[node, neighbor]['stress']
        edges[node].append([neighbor, happiness, stress])

        # print("node", node, "neighbor", neighbor, "happiness/stress", happiness / stress)
        # G.add_edge(node, neighbor, weight=happiness / stress, label='ratio')
    
    def getStudentInd(student, room):
        return x[student][room]

    def getStress(s1, s2):
        for edge in edges[s1]:
            if edge[0] == s2:
                return edge[2]
        
    def getHappiness(s1, s2):
        for edge in edges[s1]:
            if edge[0] == s2:
                return edge[1]


    m = Model(solver_name=CBC)
    
    #######################
    ###### Variables 
    #######################
    
    # k is number of rooms where 1 <= k <= n/2
    
    # x[i][l] = binary variable if student i is in room l
    # x = [[m.add_var(name='(x_' + str(i) + ')^' + str(l), var_type='B') for l in range(k)] for i in range(n)]
    x = [[m.add_var(name='x_' + str(i) + '_' + str(l), var_type='B') for l in range(k)] for i in range(n)]
    
    #######################
    ##### Constraints 
    #######################
    """
    n x k matrix
    x[student][room]
    Room     1 2 3 4   Student
            [1 0 0 0]    0
            [1 0 0 0]    1
            [0 0 1 0]    2
    """
    # ensures each student can only be in 1 room
    # sum from l=1...k (x_i)^l = 1 for all i
    for i in range(n):
        m += xsum(x[i][l] for l in range(k)) == 1

    # ensures that rooms have at least 2 people
    # sum from i=1...n ((x_i)^l) >= 2 for all l
    for l in range(k):
        m += xsum(x[i][l] for i in range(n)) >= 2
        
    for i in range(n):
        for j in range(i+1, n):
            print(i,j)
    # ensures that the sum of the stresses in rooms is valid
    # (x_i)^l * (x_j)^l * s_ij <= s_max / k for all i, j
    # TODO: avoid adding duplicate constraints (i, j) = (j, i)
    # TODO: find linear approximation to non linear approx
    divisor = 50
    for l in range(k):
        # m += xsum(x[i][l].obj * x[j][l].obj * getStress(i, j) for i in range(n) for j in range(i + 1, n)) <= S_MAX / k
        m += xsum((x[i][l] * getStress(i, j) + x[j][l] * getStress(i, j)) / divisor for i in range(n) for j in range(i + 1, n)) <= S_MAX / k
            # = 0, 1, 2 . 0 and 2 are fine. 1 is where its wrong. we get a half answer   

    # (x[i][l] * getStress(i, j) + x[j][l] * getStress(i, j)) / 2 <= S_MAX / k

    # optimize for happiness as our objective function
    # sum from l=1...k (x_i)^l * (x_j)^l * h_ij 
    # m.objective = maximize(xsum(x[i][l].obj * x[j][l].obj * getHappiness(i, j) for l in range(k) for i in range(n) for j in range(i + 1, n)))
    m.objective = maximize(xsum((x[i][l] * getHappiness(i, j) + x[j][l] * getHappiness(i, j)) for l in range(k) for i in range(n) for j in range(i + 1, n)))

    solution = {}
    m.max_gap = 0.05
    status = m.optimize(max_seconds=300)
    if status == OptimizationStatus.OPTIMAL:
        print('optimal solution cost {} found'.format(m.objective_value))
    elif status == OptimizationStatus.FEASIBLE:
        print('sol.cost {} found, best possible: {}'.format(m.objective_value, m.objective_bound))
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        print('no feasible solution found, lower bound is: {}'.format(m.objective_bound))
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print('solution:')
        for v in m.vars:
            if abs(v.x) > 1e-6: # only printing non-zeros
                print('{} : {}'.format(v.name, v.x))
                student_room = v.name.split('_')
                solution[int(student_room[1])] = int(student_room[2])

    pp = pprint.PrettyPrinter(indent=4)
    solution = dict(sorted(solution.items(), key=lambda item: item[1]))
    # pp.pprint(solution)
    print(solution)
    return solution, k


# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

if __name__ == '__main__':
    assert len(sys.argv) == 2
    path = sys.argv[1]
    G, s = read_input_file(path)
    D, k = solve(G, s)
    assert is_valid_solution(D, G, s, k)
    print("Total Happiness: {}".format(calculate_happiness(D, G)))
    write_output_file(D, 'outputs/small-1.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# if __name__ == '__main__':
#     inputs = glob.glob('inputs/*')
#     for input_path in inputs:
#         output_path = 'outputs/' + basename(normpath(input_path))[:-3] + '.out'
#         G, s = read_input_file(input_path)
#         D, k = solve(G, s)
#         assert is_valid_solution(D, G, s, k)
#         happiness = calculate_happiness(D, G)
#         write_output_file(D, output_path)
