"""Area ranges for towers in a Tower Defence game"""

from utilities import vector_length

__author__ = "Benjamin Martin"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"


class AbstractRange:
    """Abstractly-shaped area range area"""
    def contains(self, point):
        """(bool) Returns True iff 'point' exists within this range (from origin)"""
        raise NotImplementedError("contains must be implemented by a subclass")


class CircularRange(AbstractRange):
    """Circular-shaped area range"""
    def __init__(self, radius):
        """Constructor
        
        Parameters:
            radius (float): The radius of the circle underpinning the range
        """
        self.radius = radius

    def contains(self, point):
        """(bool) Returns True iff 'point' exists within this range (from origin)"""
        return vector_length(point) <= self.radius


class PlusRange(AbstractRange):
    """Plus-shaped area range"""
    def __init__(self, inner_radius, outer_radius):
        """
        Constructor
        
        Parameters:
            inner_radius (float): The inner radius of the plus underpinning the range 
            outer_radius (float): The outer radius of the plus underpinning the range
            
        I.e.
           ----
        ---|  |---  Inner radius is the width of the thin vertical bar,  
        |        |  outer radius is the width of the horizontal bar
        ---|  |---  These are symmetrical
           ----
        """
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

    def contains(self, point):
        """(bool) Returns True iff 'point' exists within this range (from origin)"""
        inn = self.inner_radius
        out = self.outer_radius

        x, y = point

        return (-inn < x < inn and -out < y < out) or (-out < x < out and -inn < y < inn)


class DonutRange(AbstractRange):
    """Donut shape area"""
    def __init__(self, inner_radius, outer_radius):
        """Constructor
        
        Parameters:
            inner_radius (float): The inner radius of the donut underpinning the range
            outer_radius (float): The outer radius of the donut underpinning the range
        """
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

    def contains(self, point):
        """(bool) Returns True iff 'point' exists within this range (from origin)"""
        return self.inner_radius <= vector_length(point) <= self.outer_radius
