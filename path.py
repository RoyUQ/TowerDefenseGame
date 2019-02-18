"""
Path-finding logic for navigating a grid with obstacles 
"""

#                                                  ,  ,
#                                                / \/ \
#                                               (/ //_ \_
#      .-._                                      \||  .  \
#       \  '-._                            _,:__.-"/---\_ \
#  ______/___  '.    .--------------------'~-'--.)__( , )\ \
# `'--.___  _\  /    |             Here        ,'    \)|\ `\|
#      /_.-' _\ \ _:,_          Be Dragons           " ||   (
#    .'__ _.' \'-/,`-~`                                |/
#        '. ___.> /=,|  Abandon hope all ye who enter  |
#         / .-'/_ )  '---------------------------------'
#         )'  ( /(/
#              \\ "
#               '=='

from queue import Queue

__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"


class Path:
    """A path from a start point to an end point.

    Used to generate shortest routes between two points.

    Attributes:
        start (tuple<int, int>): The starting point
        end (tuple<int, int>): The ending point
        deltas (dict<tuple<int, int>: tuple<int, int>>): A map of the
                                                                  best path to follow
    """

    def __init__(self, start, end, get_neighbours):
        """Initialize a path from a starting point to a finishing point

        Parameters:
            start (tuple<int, int>): The starting position
            end (tuple<int, int>): The end position
            get_neighbours (func<tuple<int, int>>): A function which takes a
                                                    position and returns the
                                                    neighbours
        """
        self.start = start
        self.end = end
        self.get_neighbours = get_neighbours

        self._generate()

    def _generate_distance_map(self):
        """Generate a mapping of positions to their distance from the end point

        Returns:
            dict<tuple<int, int>: int>: the position distance mapping
        """
        boundary = Queue()
        boundary.put(self.end)

        distances = {self.end: 0}

        # Generate distance map
        while not boundary.empty():
            to = boundary.get()

            for from_ in self.get_neighbours(to, from_=False):
                if from_ not in distances:
                    boundary.put(from_)
                    distances[from_] = distances[to] + 1

        return distances

    def _generate_best_neighbours(self, distances):
        """Calculate the best route based on a distance mapping

        Parameters:
            distances (dict<tuple<int, int>: int>): A map of positions to
                                                    distances from end point

        Returns:
            dict<tuple<int, int>: tuple<int, int>>: A map of the best path to follow
        """
        best_neighbours = {}

        # Calculate best neighbours
        for from_ in distances:
            neighbours_by_distance = []
            for to in self.get_neighbours(from_, from_=True):
                neighbours_by_distance.append((distances[to], to))

            neighbours_by_distance.sort(key=lambda x: x[0])

            best_distance = neighbours_by_distance[0][0]
            best_deltas = set()
            for distance, neighbour in neighbours_by_distance:
                if distance == best_distance:
                    delta = tuple(a - b for a, b in zip(neighbour, from_))
                    best_deltas.add(delta)

            best_neighbours[from_] = best_deltas

        del best_neighbours[self.end]

        return best_neighbours

    def _generate(self):
        """Calculate the best path to travel through the path"""
        distances = self._generate_distance_map()

        # ensure the start point can be reached from the end point
        if self.start not in distances:
            raise KeyError("Cannot reach end from start")

        self.deltas = self._generate_best_neighbours(distances)

        # overwrite bests on path
        best_path = list(self.get_best_path())

        best_path[-1] = best_path[-1][0], best_path[-2][1]

        # for cell in self.deltas:
        #     self.deltas[cell] = {self.deltas[cell].pop()}

        for best, delta in best_path:
            self.deltas[best] = {delta}

    def get_best_path(self):
        """Yields (position, delta) pairs on best path, from start to end
        
        Yield:
            (position, delta) pair:
                - position (tuple<int, int>): (column, row) position of point on the path 
                - delta (tuple<int, int>): change in (column, row) position to reach next point on path,
                                           else None iff delta == end 
        """
        best = self.start

        for delta in self.get_best_deltas():
            yield best, delta
            best = tuple(a + b for a, b in zip(best, delta))

        yield best, None

    def get_best_deltas(self):
        """Yield the best path to travel from start to finish

        Yields:
            tuple<int, int>: The best sequence of positions to reach the end
        """
        best = self.start
        previous = None

        while best != self.end:
            delta = self.get_best_delta(best, previous=previous)
            yield delta
            previous = delta
            best = tuple(a + b for a, b in zip(best, delta))

    def get_shortest(self):
        """Yield the best path to travel from start to finish

        Yields:
            tuple<int, int>: The best sequence of positions to reach the end
        """
        for best, delta in self.get_best_path():
            yield best
            if delta is None:
                break

    def get_best_delta(self, cell, previous=None):
        """(tuple<int, int>) Returns change in (column, row) position to reach next point on path
        
        Parameters:
            cell (tuple<int, int>): Current point on the path
            previous (tuple<int, int>): Previous point on the path
        """
        if previous and previous in self.deltas[cell]:
            return previous
        return next(iter(self.deltas[cell]))

    def get_sources(self, destination):
        """Yields the cell(s) that flow into destination
        
        Parameters:
            destination (tuple<int, int>): The destination cell 
        """

        for source, deltas in self.deltas.items():
            for delta in deltas:
                next_ = tuple(a + b for a, b in zip(source, delta))

                if next_ == destination:
                    yield source
