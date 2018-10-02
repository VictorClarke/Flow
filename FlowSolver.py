__author__ = 'Victor'
from collections import deque
import copy
import cv2
from heapq import heappush, heappop


class Puzzle(object):
    def __init__(self):
        filename = input("Filename: ")
        f = open(filename,"r")
        lines = f.readlines()
        f.close()
        count = 0
        self.colors = len(lines)-1
        self.locations = dict()
        for line in lines:
            if count == 0:
                split_line = line.split('X')
                self.width = int(split_line[0])
                self.height = int(split_line[1])
                count+=1
            else:
                current_color = line.split("=")[0]
                start_coordinate = eval(line.split("=")[1])
                end_coordinate = eval(line.split("=")[2])
                self.locations[current_color] = (start_coordinate, end_coordinate)

    def distance(self, color):
        start, end = self.locations[color]
        row1, column1 = start
        row2, column2 = end
        return abs(row1-row2)+abs(column1-column2)

    def ordering(self):
        distances = dict()
        for color in self.locations:
            distances[color] = self.distance(color)
        return sorted(distances, key=distances.get)

    def solvePuzzle(self):
        global maze
        maze = []
        for r in range(self.height):
            row_list = []
            for c in range(self.width):
                row_list.append("_")
            maze.append(row_list)
        for color in self.locations:
            start, end = self.locations[color]
            row1, column1 = start
            row2, column2 = end
            maze[row1][column1] = color
            maze[row2][column2] = color
        for color in self.ordering():
            start, end = self.locations[color]
            row1, column1 = start
            row2, column2 = end
            begin = MazeState(row1, column1)
            goal = MazeState(row2, column2)
            agent = SimpleSearchAgent()
            maze[row2][column2] = '_'
            moves = agent.plan(begin, goal)
            maze[row2][column2] = color
            self.fill(color, moves)
            print(maze)

    def initial_borders(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.count_neighbors(self[i][j]) <= 3:
                    self.borders.append(self[i][j])
        return self.borders

    def count_neighbors(self, location):
        count = 0
        if location.row+1 in self:
            count += 1
        if location.row-1 in self:
            count += 1
        if location.column+1 in self:
            count += 1
        if location.column-1 in self:
            count += 1
        return count
    # NEED TO REMEMBER TO ACCOUNT SELF.LOCATIONS AS PART OF BORDER UNLESS COLOR=GOAL

    def secondSolvePuzzle(self):
        global maze
        maze = []
        global past_moves
        past_moves = []
        for r in range(self.height):
            row_list = []
            for c in range(self.width):
                row_list.append("_")
            maze.append(row_list)
        for color in self.locations:
            start, end = self.locations[color]
            row1, column1 = start
            row2, column2 = end
            maze[row1][column1] = color
            maze[row2][column2] = color
        for color in self.ordering():
            start, end = self.locations[color]
            row1, column1 = start
            row2, column2 = end
            begin = MazeState(row1, column1)
            goal = MazeState(row2, column2)
            agent1 = SimpleSearchAgent()
            agent2 = HeuristicSearchAgent()
            try:
                maze[row2][column2] = '_'
                moves = agent1.plan_border(begin, goal)
                past_moves.append(moves)
                maze[row2][column2] = color
                self.fill(color, moves)
                print(maze)
            except TypeError:
                moves = agent1.plan(begin, goal)
                past_moves.append(moves)
                maze[row2][column2] = color
                self.fill(color, moves)
                print(maze)

    def make_borders(self):
        pass

    def fill(self, color, moves):
        global maze
        start, end = self.locations[color]
        row1, column1 = start
        begin = MazeState(row1, column1)
        for move in moves:
            begin = begin.neighbor(move)
            maze[begin.row][begin.column] = color
            # FIX SO THAT EACH MOVE IS CHECKED

    def bottleneck(self, color, location):
        pass

    def trapped(self):
        pass

    def undo(self, color, location):
        pass


class MazeState(object):
    # Set up a location within the maze layout.
    def __init__(self, row, column):    # Constructor
        self.row = row
        self.column = column

    # Print the maze
    def display(self):
        for r in range(len(maze)):
            for c in range(len(maze[r])):
                print(maze[r][c], end=' ')
            print()
        print()

    # Return a list of moves available in this state.
    # Possible moves are up, down, left, and right.
    def moves(self):
        moves = list()
        if self.row > 0 and maze[self.row-1][self.column] == '_':
            moves.append('up')
        if self.row < len(maze)-1 and maze[self.row+1][self.column] == '_':
            moves.append('down')
        if self.column > 0 and maze[self.row][self.column-1] == '_':
            moves.append('left')
        if self.column < len(maze[self.row])-1 and maze[self.row][self.column+1] == '_':
            moves.append('right')
        return moves

    # Return another state like this one but with one move made.
    def neighbor(self, move):
        if move == 'up':
            return MazeState(self.row-1, self.column)
        if move == 'down':
            return MazeState(self.row+1, self.column)
        if move == 'left':
            return MazeState(self.row, self.column-1)
        if move == 'right':
            return MazeState(self.row, self.column+1)


    # These methods make equivalent states be recognized as == (similar to say ".equals()")
    def __hash__(self):         # hash method; whenever you do equals and not-equals you have to include a hash method
        return hash((self.row, self.column))

    def __eq__(self, other):    # (similar to say ".equals()")
        return self.row == other.row and self.column == other.column

    def __ne__(self, other):    # like saying is opposite
        return not self == other        # But you cant say != bc it would be circular


    #define a less than method here for the case where states have the same heurisitic value
    def __lt__(self, other):
        return abs(self.row - other.row) + abs(self.column - other.column)

# Return the distance from this state to the other state
    def distance(self):
        return Puzzle.dist


class SimpleSearchAgent(object):
    # pseudo code from notebook implemented
    def plan(self, start, goal):

        # create an empty dictionary
        plan = dict()
        plan[start] = list()

        frontier = deque()
        frontier.append(start)      # put the state on the end of the queue as initial state

        while len(frontier) > 0:
            parent = frontier.popleft()     # parent is going to be a MazeState object
            for move in parent.moves():
                child = parent.neighbor(move)

                if child not in plan:
                    plan[child] = plan[parent] + [move]     # python adds lists together into one list and creates a copy automatically

                    frontier.append(child)
                    if child == goal:
                        return plan[child]

    def plan_border(self, start, goal):
        plan = dict()
        plan[start] = list()
        frontier = deque()
        frontier.append(start)

        while len(frontier) > 0:
            parent = frontier.popleft()
            for move in parent.moves():
                if parent.neighbor(move) in Puzzle.borders: # FIX
                    child = parent.neighbor(move)

                    if child not in plan:
                        plan[child] = plan[parent] + [move]
                        frontier.append(child)
                        if child == goal:
                            return plan[child]


# An agent that uses A* search to escape the maze
class HeuristicSearchAgent(object):
    def plan(self, start, goal):
        plan = dict()
        plan[start] = list()

        # For a regular queue we used a deque; for priority queue we're using heapq
        frontier = list()
        # heappush(frontier, (priority, item))
        heappush(frontier, (start.distance(goal), start))
        # finished set
        finished = set()    # similar to a hash-table

        while len(frontier) > 0:
            (priority, parent) = heappop(frontier)       # this takes the parent of the frontier
            finished.add(parent)
            # now check if the parent is the goal
            if parent == goal:
                return plan[goal]
            for move in parent.moves():
                child = parent.neighbor(move)
                if child not in finished:
                    if child not in plan or len(plan[parent]) +1 <len(plan[child]):
                        plan[child] = plan[parent] + [move]
                        # heappush(frontier, (priority, child))
                        heappush(frontier, (len(plan[child]) + child.distance(goal), child))


puzzle = Puzzle()
puzzle.secondSolvePuzzle()
maze1 = MazeState(0, 0)
maze1.display()
print()



