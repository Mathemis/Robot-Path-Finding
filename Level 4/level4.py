import numpy as np
import cv2 as cv
import math
import time
import collections
import random
import ctypes

# row ~ y axis ; column ~ x axis
# point P in input ~ maze[P[1], P[0]]
# value in Maze and Color in BGR
# -1  | border       | (115, 115, 115) 
#  0  | none         | (0, 0, 0)
#  1  | start point  | (6, 255, 248)
#  2  | goal point   | (0, 0, 255)
#  3  | pickup point | (0, 255, 255)
#  4  | route        | (255, 210, 77)
# >=5 | polygon      | random color


# === READ INPUT ===
nameInfile = input("Input file name: ")
inFile = open(nameInfile, "r")
col, row = list(map(int, inFile.readline().split(',')))
line = list(map(int, inFile.readline().split(',')))
S = (line[1], line[0]) 
G = (line[3], line[2])
Pi = line[4:]
nPo = list(map(int, inFile.readline().split()))[0]
Po = [[]] * nPo
for i in range(nPo):
    Po[i] = list(map(int, inFile.readline().split(',')))
speed = list(map(int, inFile.readline().split()))[0]
inFile.close()

boxSize = 27
img = np.ones(((row + 1) * boxSize, (col + 1) * boxSize, 3), 'uint8') * 255
maze = np.zeros((row + 1, col + 1), dtype='int8')

# === HELPER ===
def drawPoint(x, y, val):
    y = row - y
    v1 = (x * boxSize, y * boxSize)
    v2 = ((x + 1) * boxSize, (y + 1) * boxSize)
    color = (0, 0, 0)
    cv.rectangle(img, v1, v2, color)
    if val != 0:
        t1 = list(v1); t2 = list(v2)
        t1[0] += 1; t1[1] += 1
        t2[0] -= 1; t2[1] -= 1
        v1 = tuple(t1)
        v2 = tuple(t2)
        color = (0, 222, 255)
        font = cv.FONT_HERSHEY_SIMPLEX
        org = (x * boxSize + 5, y * boxSize + 21)
        if val == -1:
            color = (115, 115, 115)
            cv.rectangle(img, v1, v2, color, -1)
        elif val == 1:
            cv.rectangle(img, v1, v2, color, -1)
            cv.putText(img, 'S', org, font, 0.75, (0, 0, 0), 2, cv.LINE_AA)
        elif val == 2:
            color = (0, 119, 255)
            cv.rectangle(img, v1, v2, color, -1)
            cv.putText(img, 'G', org, font, 0.75, (0, 0, 0), 2, cv.LINE_AA)
        elif val == 3:
            color = (0, 255, 255)
            cv.rectangle(img, v1, v2, color, -1)
        elif val == 4:
            color = (255, 210, 77)
            cv.rectangle(img, v1, v2, color, -1)
            cv.putText(img, "r", org, font, 0.75, (0, 0, 0), 2, cv.LINE_AA)
        elif val >= 5:
            color = (int(val * 10) % 250, int(val * 50) % 250, int(val * 200) % 250)
            cv.rectangle(img, v1, v2, color, -1)

def round(x):
    if x - math.floor(x) >= math.ceil(x) - x:
        return math.ceil(x)
    return math.floor(x)

def makeLine(p1, p2, k):
    if (p1[0] == p2[0]):
        for i in range(min(p1[1], p2[1]), max(p1[1], p2[1]) + 1):
            maze[i, p1[0]] = k
        return
    if (p1[1] == p2[1]):
        for i in range(min(p1[0], p2[0]), max(p1[0], p2[0]) + 1):
            maze[p1[1], i] = k
        return
    a = (p1[1] - p2[1]) / (p1[0] - p2[0])
    b = p1[1] - a * p1[0]
    for i in range(min(p1[0], p2[0]), max(p1[0], p2[0]) + 1):
       maze[round(a * i + b), i] = k
    for i in range(min(p1[1], p2[1]), max(p1[1], p2[1]) + 1):
       maze[i, round((i - b) / a)] = k


# === INIT ===
# start point
maze[S] = 1
# goal point  
maze[G] = 2  
# pickup point
for i in range(0, len(Pi), 2):
    maze[Pi[i+1], Pi[i]] = 3
# polygon
for i in range(nPo):
    for j in range(0, len(Po[i]), 2):
        maze[Po[i][j + 1], Po[i][j]] = 5 + i
for i in range(nPo):
    for j in range(0, len(Po[i])-3, 2):
        makeLine(Po[i][j:j + 2], Po[i][j + 2:j + 4], i + 5)
    makeLine(Po[i][-2:], Po[i][0:2], i + 5)
# fill border in maze
for i in range(row + 1):
    maze[i, 0] = maze[i, col] = -1
for i in range(col + 1):
    maze[0, i] = maze[row, i] = -1
# draw graph
for i in range(0, col + 1):
    for j in range(0, row + 1):
        drawPoint(i, j, maze[j, i])

# Using BFS to find route
dx = [0,-1, 0, 1,-1,-1, 1, 1]
dy = [1, 0,-1, 0, 1,-1,-1, 1]
def bfs(maze, start):
    queue = collections.deque([[start]])
    seen = set()
    seen.add(start)
    while queue:
        path = queue.popleft()
        r, c = path[-1]
        if maze[r, c] == 2:
            return path
        for k in range(8):
            i = r + dy[k]
            j = c + dx[k]
            if 0 < j < col and 0 < i < row:
                if (maze[i][j] == 0 or maze[i][j] == 2) and (i, j) not in seen:
                    # Skip step that go through the polygon
                    if k > 3:
                        if k == 4 and maze[i, j + 1] == maze[i - 1, j] and maze[i - 1, j] >= 5:
                            continue
                        if k == 5 and maze[i, j + 1] == maze[i + 1, j] and maze[i + 1, j] >= 5:
                            continue
                        if k == 6 and maze[i, j - 1] == maze[i + 1, j] and maze[i + 1, j] >= 5:
                            continue
                        if k == 7 and maze[i, j - 1] == maze[i - 1, j] and maze[i - 1, j] >= 5:
                            continue
                    queue.append(path + [(i, j)])
                    seen.add((i, j))


move = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
        # up    left-top   left  left-bottom  down  right-bot  right  right-top
def movePolygons():
    for k in range(5, nPo + 5):
        step = random.randint(1, 100) % 4 * 2
        dr = move[step][0]
        dc = move[step][1]
        collision = False
        for r in range(1, row):
            for c in range(1, col):
                if maze[r][c] == k:
                    if 0 < r + dr < row and 0 < c + dc < col:
                        if maze[r + dr][c + dc] in [-1, 1, 2, 4] or (maze[r + dr][c + dc] >= 5 and maze[r + dr][c + dc] != k):
                            collision = True
                            break
                    else:
                        collision = True
                        break               
            if collision:
                break
        if collision == False:
            if step < 3:
                for r in range(row - 1, 0, -1):
                    for c in range(1, col):
                        if maze[r][c] == k and 0 < r + dr < row and 0 < c + dc < col:
                            maze[r][c] = 0
                            maze[r + dr][c + dc] = k
            elif step == 3:
                for r in range(1, row):
                    for c in range(1, col):
                        if maze[r][c] == k and 0 < r + dr < row and 0 < c + dc < col:
                            maze[r][c] = 0
                            maze[r + dr][c + dc] = k    
            elif step < 7:
                for r in range(1, row):
                    for c in range(col - 1, 0, -1):
                        if maze[r][c] == k and 0 < r + dr < row and 0 < c + dc < col:
                            maze[r][c] = 0
                            maze[r + dr][c + dc] = k
            else:
                for r in range(row - 1, 0, -1):
                    for c in range(col - 1, 0, -1):
                        if maze[r][c] == k and 0 < r + dr < row and 0 < c + dc < col:
                            maze[r][c] = 0
                            maze[r + dr][c + dc] = k


def updateGraph():
    for i in range(0, col + 1):
        for j in range(0, row + 1):
            drawPoint(i, j, maze[j, i])

# Check if can go from p1(r1, c1) to p2(r2, c2) or not
# p1, p2 is already in the maze 
def canGo(maze, p1, p2):
    d = (p2[1] - p1[1], p2[0] - p1[0])
    i, j = p2[0], p2[1]
    if maze[p2] == 0 or maze[p2] == 2:
        # Skip step that go through the polygon
        if (d == (-1, 1) and maze[i, j + 1] == maze[i - 1, j] and maze[i - 1, j] >= 5) or \
           (d == (-1,-1) and maze[i, j + 1] == maze[i + 1, j] and maze[i + 1, j] >= 5) or \
           (d == ( 1,-1) and maze[i, j - 1] == maze[i + 1, j] and maze[i + 1, j] >= 5) or \
           (d == ( 1, 1) and maze[i, j - 1] == maze[i - 1, j] and maze[i - 1, j] >= 5):
            return False
        return True
    return False

# cost between two point
def calCost(p1, p2):
        t = (route[0][0] - prevS[0], route[0][1] - prevS[1])
        if t in move[::2]:
            return 1.0
        return 1.5

# cost of route
cost = 0
count = 0
prevS = None
route = bfs(maze, S)
if route == None:
    count += 1
else:
    route = collections.deque(route)
    isDeque = True
    prevS = route.popleft()
    if len(route) < 2:
        ctypes.windll.user32.MessageBoxW(0, "GO TO GOAL SUCESSFULLY!", "Message", 1)
        cv.destroyAllWindows()
    elif canGo(maze, prevS, route[0]):  # go next
        cost += calCost(prevS, route[0])
        maze[route[0]] = 4
prev = route[0]

# cv.namedWindow("Robot find route", cv.WINDOW_NORMAL)
cv.imshow("Robot find route", img)
print("Press Enter to run...")
# wait until press Enter
while cv.waitKey(0) != 13:
    pass



updateGraph()
cv.imshow("Robot find route", img)

# cv.imwrite("pic0.jpg", img)



jump = False
while cv.waitKey(1000 // speed) != ord('q') and cv.getWindowProperty("Robot find route", 0) >= 0:
    if count > 1000:
        ctypes.windll.user32.MessageBoxW(0, "CAN'T FIND ROUTE!", "Message", 1)
        break
    if route == None: # got stuck
        count += 1
        route = bfs(maze, prevS) # find new route
        if route == None:
            movePolygons()
        else:
            count = 0
            route = collections.deque(route)
            jump = True
    else:
        jump = True
    if jump:
        jump = False
        movePolygons()
        prevS = route.popleft()
        if len(route) < 2:
            ctypes.windll.user32.MessageBoxW(0, "GO TO GOAL SUCESSFULLY!", "Message", 1)
            break
        if canGo(maze, prevS, route[0]):  # if can go to next point, delete prev, go next
            maze[prevS] = 0
            maze[route[0]] = 4
            cost += calCost(prevS, route[0])
        else: # stuck, clear old route
            route = None
    
    img = np.ones(((row + 1) * boxSize, (col + 1) * boxSize, 3), 'uint8') * 255
    updateGraph()
    cv.imshow("Robot find route", img)

# print total cost to output file
outFile = open("output.txt", "w+")
outFile.write("%f" % cost)
outFile.close()

cv.destroyAllWindows()