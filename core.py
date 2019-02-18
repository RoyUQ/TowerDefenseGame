"""Low-level core classes for basic tower defence game"""

import math
from abc import ABC

__author__ = "Benjamin Martin"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"


class Unit(ABC):
    """A basic unit on the game field"""
    name: str
    colour: str

    # See:
    #  - https://louisem.com/29880/color-thesaurus-infographic
    #  - http://mentalfloss.com/article/53121/11-colors-youve-probably-never-heard

    def __init__(self, position, grid_size, cell_size):
        self.position = position
        self.grid_size = grid_size

        self.cell_size = None
        self.size = None
        self.set_cell_size(cell_size)

    def set_cell_size(self, cell_size: int):
        """Sets the cell size for this unit to 'cell_size'"""
        self.size = tuple(i * cell_size for i in self.grid_size)
        self.cell_size = cell_size

    def move_by(self, delta):
        """Moves by 'delta'"""
        x, y = self.position
        dx, dy = delta
        self.position = x + dx, y + dy

    def get_bounding_box(self):
        """Returns the bounding box of this unit, as a pair of coordinate pairs: 
        ((left, top), (right, bottom))
        """
        x, y = self.position
        if x is None:
            return None

        width, height = self.size
        x0, y0 = x - width // 2, y - height // 2
        x1, y1 = x0 + width, y0 + height

        return (x0, y0), (x1, y1)


class Point2D:
    """A 2-dimensional point"""
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """(Point2D) Returns result of adding 'other' to this point"""
        return Point2D(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        """Internally adds 'other' to this point"""
        self.x += other.x
        self.y += other.y

    def __sub__(self, other):
        """(Point2D) Returns result of subtracting 'other' from this point"""
        return Point2D(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        """Internally subtracts 'other' from this point"""
        self.x -= other.x
        self.y -= other.y

    def __floordiv__(self, divisor):
        """(Point2D) Returns result of integer dividing this point by 'divisor'"""
        return Point2D(self.x // divisor, self.y // divisor)

    def __truediv__(self, divisor):
        """(Point2D) Returns result of dividing this point by 'divisor'"""
        return Point2D(self.x / divisor, self.y / divisor)

    def __mul__(self, factor):
        """(Point2D) Returns result of multiplying 'factor' by this point"""
        return Point2D(self.x * factor, self.y * factor)

    def __rmul__(self, other):
        """(Point2D) Returns result of multiplying this point by 'factor'"""
        return Point2D(self.x * other, self.y * other)

    def __iter__(self):
        """Yields coordinates of this point; first then second"""
        yield self.x
        yield self.y

    def __str__(self):
        """(str) Returns a string representation of this point"""
        return str("Point2D({!r}, {!r})".format(self.x, self.y))

    def __gt__(self, other):
        """(bool) Returns True iff all coordinates in this point are greater than the corresponding
        coordinates in 'other'"""
        return self.x > other.x and self.y > other.y

    def __le__(self, other):
        """(bool) Returns True iff all coordinates in this point are less than or equal to the
        corresponding coordinates in 'other'"""
        return self.x <= other.x and self.y <= other.y

    def rotate(self, angle):
        """Rotates by 'angle' radians

        Parameters:
            angle (num): The angle by which to rotate
        """
        cos = math.cos(angle)
        sin = math.sin(angle)

        x = self.x
        y = self.y

        self.x = cos * x - sin * y
        self.y = sin * x + cos * y

    def tuple(self):
        """(num, num) Returns the tuple form of this point"""
        return self.x, self.y


class BucketManager:
    """Collection of values mapped from two dimensional positions in a grid, the grid
    divided into multiple buckets (sub-regions)"""

    def __init__(self, max_position, buckets=(10, 10)):
        bucket_size = tuple(int(i / buckets_i + .5) for i, buckets_i in zip(max_position, buckets))

        self._max = max_position
        self._buckets = [[set() for i in range(buckets[1])] for i in range(buckets[0])]
        self._bucket_size = bucket_size

    def clear(self):
        """Removes all value & position mappings"""
        for column in self._buckets:
            for cell in column:
                cell.clear()

    def position_to_index(self, position):
        """(tuple<int, int>) Returns index of the bucket that corresponds to position
        
        Parameters:
            position (tuple<int, int>): The position in the grid
        """
        return tuple(int(i // i_bucket_size) for i, i_bucket_size in zip(position, self._bucket_size))

    def add(self, position, value):
        """(tuple<int, int>) Adds 'value' at 'position'
        
        Parameters:
            position (tuple<int, int>): The position in the grid
            value (*): The value to add
        """
        x_i, y_i = self.position_to_index(position)
        self._buckets[x_i][y_i].add(value)

    def get_bucket_for_position(self, position):
        """(tuple<int, int>) Returns the bucket corresponding to 'position'
        
        Parameters:
            position (tuple<int, int>): The position in the grid
        """
        x_i, y_i = self.position_to_index(position)
        return self._buckets[x_i][y_i]

        # def get_nearby_buckets(self):

    def get_closish(self, position, nearby_buckets=None):
        """Yields positions, roughly prioritised by proximity to 'position'"""
        raise NotImplementedError("get_closish must be implemented by a subclass")


class UnitManager(BucketManager):
    """Collection of Units mapped from their two dimensional positions in a grid, the grid
    divided into multiple buckets (sub-regions)"""

    def add_unit(self, unit: Unit):
        """Adds 'unit' to this UnitManager"""
        self.add(unit.position, unit)

    def get_closish(self, position, nearby_buckets=None):
        """Yields positions, roughly prioritised by proximity to 'position'"""
        # naive implementation, performance could be improved by searching outwards from nearby buckets

        # if nearby_buckets is None:
        #     nearby_buckets = {(0, 0)}

        # x_i, y_i = self.position_to_index(position)

        for column in self._buckets:
            for values in column:
                for value in values:
                    yield value


class GameData:
    """Class to hold data in a game without granting unrestricted access to top-level
    modelling class directly"""

    enemies = None
    obstacles = None
    towers = None
    grid = None
    path = None
