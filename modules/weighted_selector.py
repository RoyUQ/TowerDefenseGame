"""
Dictionary-like data structure, mapping keys to probability weights, which
provides efficient random selection
"""
import itertools
import bisect
import random

__author__ = "Benjamin Martin"
__copyright__ = "Copyright 2017, The University of Queensland"
__license__ = "MIT"
__date__ = "26/09/2017"
__version__ = "1.0.2"


class WeightedSelector:
    """Provides random choice between multiple choices, according to their
    relative probability weights

    Preconditions:
        Any probability weighting for a choice is non-negative

    Time Complexity:
        Provided dictionary in/get/set runs in amortized O(1) time;

        __setitem__ runs in O(1) time iff the (choice, weight) pair would not
        result in a change

        update, __setitem__, & __delitem__ run in O(n) time, where n is the
        total number of choices in the WeightedSelector
    """

    def __init__(self, choices):
        """
        Constructor

        Parameters:
            choices (dict<*, num>): Map of choices to probability weights
        """

        self._p_values = []
        self._weights = {}
        self._values = ()
        self.update(choices)

    def __setitem__(self, choice, weight):
        """Sets the weight corresponding to a given choice, unless doing so
        would result in no change"""
        if choice in self._weights and self._weights[choice] == weight:
            return

        self._weights[choice] = weight
        self._generate_p()

    def __delitem__(self, choice):
        """Deletes the weight corresponding to a given choice, unless choice
        does not exist"""
        if choice not in self._weights:
            return
        del self._weights[choice]
        self._generate_p()

    def update(self, choices, clear=False):
        """
        Updates by adding overwriting or clearing existing choices

        Parameters:
            choices (dict<*, num>): Map of choices to probability weights
            clear (bool): If True, existing choices are cleared
        """
        if clear:
            self._weights.clear()
        self._weights.update(choices)
        self._generate_p()

    def _generate_p(self):
        """Generates cumulative p values for each choice"""
        self._values, weights = zip(*self._weights.items())
        cumsum = list(itertools.accumulate(weights))
        total = cumsum[-1]
        self._p_values = [i / total for i in cumsum]

    def choose(self):
        """(*) Returns a random choice"""

        i = bisect.bisect(self._p_values, random.random())
        return self._values[i]

    def clone(self):
        """(WeightedSelector) Returns a clone of this object"""

        return WeightedSelector(self._weights)

    @classmethod
    def from_equals(cls, choices):
        """(WeightedSelector) Returns a new weighted selector from equal choices

        Parameters:
            choices (list<*>): A sequence of choices to be given equal weights
        """
        return cls({choice: 1 for choice in choices})
