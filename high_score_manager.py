"""Classes to assist in managing high scores"""

import json

__author__ = "Benjamin Martin"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"

DEFAULT_GAME = 'basic'


class HighScoreManager:
    """Manages high scores across multiple game types & persists to file"""
    _data = None
    _top_scores = 10  # The number of scores on each leader board

    def __init__(self, filename='high_scores.json'):
        self._filename = filename
        self.load(filename)

    def load(self, filename):
        """Loads high scores from file
        
        Parameters:
            filename (str): The filename of the file to load from
        """
        try:
            with open(filename) as file:
                self._data = json.load(file)
        except FileNotFoundError:
            self._data = {}

    def save(self, filename=None):
        """Saves highs cores to file
        
        Parameters:
            filename (str): The filename of the file to save to
                            If None, saves to the same file that was loaded
        """
        if filename is None:
            filename = self._filename

        with open(filename, 'w') as file:
            json.dump(self._data, file)

    def get_lowest_score(self, game=DEFAULT_GAME):
        """Gets lower score on the high score board
        
        Parameters:
            game (str): Unique ID for the high score board
             
        Return:
            (int): The lowest score on the board, else None if the board is empty
        """
        entries = self._data.get(game)

        if entries is None:
            return None

        return entries[-1]['score']

    def does_score_qualify(self, score, game=DEFAULT_GAME):
        """(bool) Returns True iff score qualifies to be added to high score board
        
        Existing scores win ties
        
        Parameters:
            game (str): Unique ID for the high score board
        """
        if score == 0:
            return False

        lowest = self.get_lowest_score(game=game)

        if lowest is None:
            return True

        return len(self._data.get(game)) < self._top_scores or score > lowest

    def add_entry(self, name, score, data=None, game=DEFAULT_GAME):
        """Adds an entry to the high score board
        
        Parameters:
            name (str): The player's name
            score (int): The player's score
            data (*): Extra data to store with the entry
            game (str): Unique ID for the high score board
             
        Preconditions:
            score qualifies for addition to the board
        """
        if game not in self._data:
            self._data[game] = []

        entries = self._data[game]

        entries.append({
            'name': name,
            'score': score,
            'data': data
        })

        entries.sort(key=lambda entry: entry['score'], reverse=True)

        if len(entries) > self._top_scores:
            return entries.pop()

        return None

    def get_entries(self, game=DEFAULT_GAME):
        """Gets all entries on high score board, sorted by ascending rank (1st, 2nd, ...)
        
        Parameters:
             game (str): Unique ID for the high score board
             
        Return:
            dict: {
                'name': The player's name,
                'score': The player's score,
                'data': Extra data stored with the entry
            }
        """
        return self._data.get(game, [])
