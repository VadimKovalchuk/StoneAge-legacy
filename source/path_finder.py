from source import tools
import pygame
import math

#CONSTANTS
#Uplading constants from setup.ini file
constants = tools.Constants()
'''___________________________________________________________'''
#Number of cells by X and Y axises
LAND_NUM_Y      = constants['LAND_NUM_Y']       #Default 4
LAND_NUM_X      = constants['LAND_NUM_X']       #Default 6
#Land cell types
FIELD = constants['FIELD']      #Default is 'field'
FOREST = constants['FOREST']    #Default is 'forest'
MOUNTAIN = constants['MOUNTAIN']#Default is 'mountain'
WATER = constants['WATER']      #Default is 'water'
CAMP = constants['CAMP']        #Default is 'camp'
del constants

PATHFINDER_DEBUG = False
'''___________________________________________________________'''

class PathFinder:
    """ Class for finding the path across the map. Calculates new paths
    and stores them for future uses"""

    def __init__(self, map):
        '''
        (list of lists) -> NoneType

        Builds initial logical map where impassable tile is
        a "wall"(mountain, river or camp) and 1 is a passable territory.
        Path collection is a dictionary of dictionaries of lists of tuples
        where:
            - first dictionary value is start point
            - second dictionary value is end point
            - list is a waypoint where
            - each tuple is coordinate
        '''
        self.map = map
        self.path_collection = {}
        #Internal variables
        self.logical_map = []
        self.processing_map = []
        self.start = ()
        self.end = ()
        self.call_counter = 0

        self.reinit()

        return None

    def reinit(self):
        '''
        (None) -> None

        Build basic logical map
        '''
        for x in range(0,LAND_NUM_X):
            y_line = []
            for y in range(0,LAND_NUM_Y):
                if self.map[x][y].land_type in [FIELD,FOREST]:
                    y_line.append(1)
                else:
                    y_line.append(0)
            self.logical_map.append(y_line[:])
            self.processing_map.append(y_line[:])

        self.path_collection = {}


    def get_path(self, start, end):
        '''
        ((int, int),(int, int)) -> list of tuples
        '''
        #If path exists than it will be returned
        if start in self.path_collection:
            if end in self.path_collection[start]:
                return self.path_collection[start][end][:]

        #If path does not exists than new waypoint will be calculated.
        #Creating entry in self.path_collection
        if PATHFINDER_DEBUG: print("Calculating path:",start,'->',end)
        if start not in self.path_collection:
            self.path_collection[start] = {}

        #Setting start and end point
        self.start = start
        self.end = end
        self._prepare_search()
        start_time = pygame.time.get_ticks()

        #Initiating recursion to find the path(recursion depth is
        #increased if path not found
        final_depth = 4
        for recursion_depth in range(4,13):
            waypoint = self._searcher(start,recursion_depth,[])
            if waypoint:
                final_depth = recursion_depth
                break
        end_time = pygame.time.get_ticks()
        if PATHFINDER_DEBUG: print("Number of recursion calls:",
                                   self.call_counter,
                                   "\nRecursion depth:",final_depth,
                                   "\nCalculation time:",end_time - start_time,
                                   "\nResulting path:",waypoint,"\n")
        self.path_collection[start][end] = waypoint

        # Reversing waypoint to build path for returning
        if end not in self.path_collection:
            self.path_collection[end] = {}
        if waypoint:
            reversed_waypoint = waypoint[:]
            reversed_waypoint.reverse()
            self.path_collection[end][start] = reversed_waypoint
        else:
            self.path_collection[end][start] = False

        return waypoint[:]

    def _searcher(self, coordinatate, iterations, visited):
        '''
        ((int, int)) -> list of tuples

        Recursive function that analyses all possible paths to destination point
        '''
        self.call_counter += 1
        if (iterations - 1) == 0:
            return False
        if coordinatate == self.end:
            return [self.end]

        visited.extend([coordinatate])
        waypoint = [coordinatate]
        collector = []
        #Virifying available alternatives in all possible directions
        # except one that arrived from or already visited
        for x in range(-1,2):
            for y in range(-1,2):
                iterable_coord = (coordinatate[0] + x,coordinatate[1] + y)
                if self._is_valid_coord(iterable_coord) and\
                    iterable_coord not in visited:
                    result = self._searcher(iterable_coord,
                                            iterations -1,visited[:])
                    if result:
                        collector.append(result)
        #Checking if any paths are found
        if (len(collector)) == 0:
            return False
        #Analyses which path is the shortest
        shortest = collector[0]
        for path in collector:
            if self._length(path) < self._length(shortest):
                shortest = path

        waypoint.extend(shortest)
        return waypoint

    def _prepare_search(self):
        '''
        (None) -> None

        Clears checked tiles and copies logical map to processed
        with setting start and end points as passable.
        '''
        for x in range(0,LAND_NUM_X):
            for y in range(0,LAND_NUM_Y):
                self.processing_map[x][y] = self.logical_map[x][y]
        (x, y)=self.start
        self.processing_map[x][y] = 1
        (x, y)=self.end
        self.processing_map[x][y] = 1
        self.call_counter = 0

        return None

    def _is_valid_coord(self, coordinate):
        '''
        ((int, int)) ->bool

        Verifies if passed coordinate is valid and if it is already
        used in previous iterations.
        '''
        (x,y) = coordinate
        if x in range(0,LAND_NUM_X) and \
            y in range(0,LAND_NUM_Y) and \
            self.processing_map[x][y]:
            return True
        else:
            return False

    def _length(self, waypoint):
        '''

        '''
        if len(waypoint) == 1:
            return 0
        length = 0
        for i in range(0,len(waypoint)-1):
            x_dif = abs(waypoint[i][0]-waypoint[i+1][0])
            y_dif = abs(waypoint[i][1]-waypoint[i+1][1])
            length += math.sqrt(math.pow(x_dif,2)+math.pow(y_dif,2))

        return length

    def _print_table(self, table):
        '''
        (list of lists) -> None

        Prints table with size LAND_NUM_X x LAND_NUM_Y
        '''
        for y in range(0,LAND_NUM_Y):
            for x in range(0,LAND_NUM_X):
                print(table[x][y],sep=' ',end='')
            print()
        print()
        return None



























