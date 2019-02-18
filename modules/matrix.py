"""
Two-dimensional matrix data structure
"""
import itertools

__author__ = "Benjamin Martin"
__copyright__ = "Copyright 2017, The University of Queensland"
__license__ = "MIT"
__date__ = "27/09/2017"
__version__ = "1.1.3"

# Change in position for all adjacent cells
RADIAL_DELTAS = tuple(
    cell for cell in itertools.product(*itertools.repeat((-1, 0, 1), 2)) if
    cell.count(0) <= 1)

# Change in position for all axially adjacent cells
AXIAL_DELTAS = tuple(cell for cell in RADIAL_DELTAS if cell.count(0) == 1)

# Change in position for all diagonally adjacent cells
DIAGONAL_DELTAS = tuple(cell for cell in RADIAL_DELTAS if cell.count(0) == 0)


def get_adjacent_cells(position, deltas=AXIAL_DELTAS, valid=lambda neighbour, position: True):
    """Yields adjacent cells from a given position

    Parameters:
        position (int, int): Position of the cell for which to find neighbours
        deltas (tuple(tuple<int, int>, ...)):
            Changes in position, each corresponding to an adjacent cell
            Defaults to AXIAL_DELTAS
        valid (callable(neighbour, position)): Returns True iff neighbour is valid as an adjacent cell to position,
                                               where neighbour & position are both cell positions (tuple<int, int>)

    Yield:
        tuple<int, int>: Position of each adjacent cell
    """
    for delta in deltas:
        neighbour = tuple(a + b for a, b in zip(position, delta))

        # ensure cell is valid
        if valid(neighbour, position):
            yield neighbour


def get_adjacent_border_pairs(cell1, cell2):
    """For a pair of adjacent cells, cell1 & cell2, yields every pair of adjacent cells such that
    the border would be connected to the border between cell1 & cell2
    
    Parameters:
        cell1 (tuple<int, int>): A cell position
        cell2 (tuple<int, int>): Another cell position adjacent to cell1
    
    Yield:
        tuple<tuple<int, int>, tuple<int, int>>: Pair of positions of border pair candidates
        
    Notes:
        For example, the border pairs adjacent to the border between (1, 0) & (1, 1) would be:
            1: ((2, 0), (1, 0)), 2: ((1, 0), (0, 0)), 3: ((0, 0), (0, 1)), 
            4: ((0, 1), (1, 1)), 5: ((1, 1), (2, 1)), 6: ((2, 1), (2, 0)) 
        
        0, 0 | 0, 1
        -----------
        1, 0 | 1, 1
        -----------
        2, 0 | 2, 1
    """
    are_horizontal = cell1[0] == cell2[0]
    deltas = [(1, 0), (-1, 0)] if are_horizontal else [(0, 1), (0, -1)]

    candidates = []
    for cell in (cell1, cell2):
        for neighbour in get_adjacent_cells(cell, deltas=deltas):
            yield cell, neighbour  # border edge turns 90 degrees (if valid)

            candidates.append(neighbour)

    for i in range(2):
        yield candidates[i], candidates[2 + i]  # border edge continues straight (if valid)


class Matrix:
    """2d grid-like data structure

    Key Terms:
        position: A (row, column) pair of coordinates
        valid position: A position that exists in the matrix"""

    RADIAL_DELTAS = RADIAL_DELTAS
    AXIAL_DELTAS = AXIAL_DELTAS
    DIAGONAL_DELTAS = DIAGONAL_DELTAS

    def __init__(self, size, default=None):
        """
        Constructor

        Parameters:-
            size (int): The number of (rows, columns)
            default (*): The default value. Defaults to None

        Preconditions:
            rows & columns are both > 0
        """
        rows, columns = size
        self._cells = [[default for _ in range(columns)] for _ in range(rows)]
        self._default = default
        self._dim = size

        self._valid_neighbour = lambda neighbour, cell: neighbour in self

    def reset(self):
        """Resets all elements in this matrix to the default"""
        rows, columns = self._dim
        for i in range(rows):
            for j in range(columns):
                self._cells[i][j] = self._default

    def size(self):
        """(tuple<int, int>) Returns the size of this matrix"""
        return self._dim

    def __contains__(self, position):
        """Returns True iff position represents a valid (row, column) pair

        Parameters:
            position (tuple<int, int>): A position to test

        Return: bool"""

        if not all(a <= b < c for a, b, c in
                   zip(itertools.repeat(0, len(self._dim)), position,
                       self._dim)):
            # Coordinates out of range
            return False

        return True

    def __getitem__(self, position):
        """(*) Returns the value corresponding to the key

        Parameters:
             position (tuple<int, int>): A position"""
        row, column = position
        return self._cells[row][column]

    def __setitem__(self, position, value):
        """Sets the value corresponding to the key

        Parameters:
             position (tuple<int, int>): A position
             value (*): The new value"""
        row, column = position
        self._cells[row][column] = value

    def __delitem__(self, key):
        """Deletes the key and corresponding value

        Parameters:
             key (tuple<int, int>): A position"""
        row, column = key
        self._cells[row][column] = None

    def keys(self):
        """Yields (row, column) positions for every cell

        Yield:
            (tuple<int, int>): (row, column) position"""
        yield from itertools.product(*(range(dim) for dim in self._dim))

    def __iter__(self):
        """Alias for .keys()"""
        return self.keys()

    def values(self):
        """Yields values for each cell 

        Yield:
            (*): Value"""
        for position in self.keys():
            yield self[position]

    def items(self):
        """Yields (key, value) pairs for every cell, where key is the
        (row, column) position

        Yield:
            (tuple<int, int>, *): (position, value) pair
        """
        for cell in self:
            yield cell, self[cell]

    def get_rows(self):
        """Yields rows of values

        Yield:
            list<*>: Values in each row
        """
        yield from self._cells

    def get_columns(self):
        """Yields columns of values

        Yield:
            list<*>: Values in each row
        """
        rows, columns = self._dim
        for column in range(columns):
            yield [self[row, column] for row in range(rows)]

    def get_adjacent_cells(self, position, deltas=AXIAL_DELTAS):
        """Yields adjacent cells from a given position

        Parameters:
            position (int, int): A position
            deltas (tuple(tuple<int, int>, ...)):
                Changes in position, each corresponding to an adjacent cell
                Defaults to AXIAL_DELTAS

        Yield:
            tuple<int, int>: Position of each adjacent cell
        """
        yield from get_adjacent_cells(position, deltas=deltas, valid=self._valid_neighbour)

    def are_cells_adjacent(self, position1, position2, deltas=AXIAL_DELTAS):
        """(bool) Returns True iff cells at position1 & position2 are adjacent
        
        Parameters:
            position1 (tuple<int, int>): The first position
            position2 (tuple<int, int>): The second position
            deltas (tuple(tuple<int, int>, ...)):
                Changes in position, each corresponding to an adjacent cell
                Defaults to AXIAL_DELTAS            
        """
        for adjacent in self.get_adjacent_cells(position1, deltas=deltas):
            if adjacent == position2:
                return True
        return False

    # pylint: disable=redefined-argument-from-local
    def serialise(self, serialiser=lambda cell: cell):
        """Serialises the matrix
        
        Return:
            tuple<list<list<*>>, *>: Pair of:
                                        0. Two-dimensional list of serialized cells - list of rows, each row being a 
                                           list of serialized cells
                                        1. Default value of grid
                                        
                                     Note: rows & columns can be inferred from dimensions of return[0]
        """
        serialised = []
        for row in self.get_rows():
            serialised_row = []
            serialised.append(serialised_row)
            for cell in row:
                serialised_row.append(serialiser(cell))

        return (serialised, self._default)

    @classmethod
    # pylint: disable=redefined-argument-from-local
    def deserialize(cls, cells, default, deserialiser=lambda cell: cell):
        """(Matrix) Returns a deserialised matrix
        
        Parameters:
            cells (list<list<*>>): Serialised cells - see docstring on Matrix.serialise
            default (*): The default value for the matrix
            deserialiser (callable): Callable to deserialise a cell
        """
        matrix = cls((len(cells), len(cells[0])), default)

        for i, row in enumerate(cells):
            for j, cell in enumerate(row):
                matrix[i, j] = deserialiser(cell)

        return matrix

    def get_cell_str(self, position):
        """Returns the value to use when creating the matrix string"""
        return self[position]

    def __str__(self):
        """Returns a human readable string of the matrix"""

        cell_strs = Matrix(self._dim)

        for position in self:
            cell_strs[position] = str(self.get_cell_str(position))

        selector = len

        max_width = selector(max(cell_strs.values(), key=selector))

        formatter = "{:<" + str(max_width) + "}"

        cell_strs = cell_strs.serialise(serialiser=formatter.format)[0]

        for i, _ in enumerate(cell_strs):
            cell_strs[i] = "| " + " | ".join(cell_strs[i]) + " |"

        divider = len(cell_strs[0]) * '-'
        return (divider + "\n") + ("\n" + divider + "\n").join(cell_strs) + ("\n" + divider)

    def get_borders(self, is_border_between=lambda cell1, cell2: False):
        """Yields list of borders, where each border a list of all pairs of cells that are on the border
        
        Parameters:
            is_border_between (callable<cell1, cell2>>): 
                    Returns True iff there is a border between cell1 & cell2,
                    where cell1 & cell2 are cell positions (tuple<int, int>)
                    
        Yield:
            list<tuple<tuple<int, int>, tuple<int, int>>>: List of cell pairs on the border, for each border
        """
        # generate set of (p1, p2) & (p2, p1) for all p1, p2 such that a border exists between p1 & p2
        border_pairs = set()
        for position in self:
            for next_position in get_adjacent_cells(position, valid=is_border_between):
                border_pairs.update({(position, next_position), (next_position, position)})

        while len(border_pairs):
            border = []

            neighbour1, neighbour2 = border_pairs.pop()
            border_pairs.remove((neighbour2, neighbour1))

            while True:

                border.append((neighbour1, neighbour2))

                # Find the find n1 & n2 pair that are a border pair, else done
                for neighbour1, neighbour2 in get_adjacent_border_pairs(neighbour1, neighbour2):
                    if (neighbour1, neighbour2) in border_pairs:
                        break  # found a next n1 & n2 pair whose border connects with current n1 & n2
                else:
                    break  # no connecting n1 & n2 pair found

                border_pairs.difference_update({(neighbour1, neighbour2), (neighbour2, neighbour1)})

            yield border
