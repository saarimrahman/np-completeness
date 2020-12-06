from parse import read_input_file, read_output_file
import random

def makeNums(n, s):
    final = []
    #  num_rooms = n // 2 
    final.append(str(n) + '\n')
    final.append(str(s) + '\n')
    for i in range(n):
        for j in range(i + 1, n):
            if i % 2 == 0 and i + 1 == j:
                final.append(str(i) + " " + str(j) + " " + str(5) + " " + str(5) + "\n")
            else:
                # if n == 20 or n == 10:
                #     x = random.randint(2500, 5000)/1000
                # if n == 50:
                #     x = random.randint(10000, 20000)/1000
                x = random.randint(2500, 5000)/1000
                final.append(str(i) + " " + str(j) + " " + str(x) + " " + str(x) + "\n")
    path = str(n) + ".in"
    with open(path, "w") as fo:
        for fin in final:
            fo.write(fin)
    fo.close()

def makeOut(n):
    final = []
    count = 0

    for i in range(0 , n//2):
        final.append(str(count) + " " + str(i) + "\n")
        final.append(str(count + 1) + " " + str(i) + "\n")
        count += 2
    path = str(n) + ".out"
    with open(path, "w") as fo:
        for fin in final:
            fo.write(fin)
    fo.close()

# makeOut(50)
# makeNums(20, 50.001)

read_input_file('10.in')
read_input_file('20.in')
read_input_file('50.in')

G, s = read_input_file('10.in')
read_output_file('10.out', G, s)

G, s = read_input_file('20.in')
read_output_file('20.out', G, s)

G, s = read_input_file('50.in')
read_output_file('50.out', G, s)