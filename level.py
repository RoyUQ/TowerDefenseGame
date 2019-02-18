"""Contains abstract level for generating waves and relevant utilities functions"""

__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"


class AbstractLevel:
    """A level in the game, with multiple waves of enemies"""
    EASY = 0
    NORMAL = 1
    HARD = 2

    waves = None

    def __init__(self, difficulty=NORMAL):
        self.difficulty = difficulty

    def get_wave(self, wave_n):
        """Returns enemies in the 'wave_n'th wave

        Parameters:
            wave_n (int): The nth wave

        Return:
            list[tuple[int, AbstractEnemy]]: A list of (step, enemy) pairs in the
                                             wave, sorted by step in ascending order 
        """
        raise NotImplementedError("get_wave must be implemented by a subclass")

    def get_max_wave(self):
        """(int) Returns the total number of waves"""
        return self.waves

    @staticmethod
    def generate_intervals(total, intervals):
        """Divides a total into even intervals
    
        Loosely equivalent to range(0, total, total/intervals), where each yield is an integer
    
        Parameters:
            total (float|int): The total to be divided into intervals
            intervals (int): The number of intervals
    
        Yield:
            int: Each interval
        """
        interval_step = total / intervals

        for i in range(intervals):
            yield int(interval_step * i)

    @classmethod
    def generate_sub_wave(cls, steps, count, enemy_class, args=None, kwargs=None, offset=0):
        """Generates a sub-wave compatible with TowerGame.queue_wave
        
        Parameters:
            steps (int): The number of steps over which to spawn this sub-wave
            count (int): The number of enemies to distribute
            enemy_class (Class<AbstractEnemy>): The enemy constructor
            args: Positional arguments to pass to the enemy's constructor
            kwargs: Keyword arguments to pass to the enemy's constructor
            offset (int): The first step (i.e. positive offset for each step)
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        for step in cls.generate_intervals(steps, count):
            yield step + offset, enemy_class(*args, **kwargs)

    @classmethod
    def generate_sub_waves(cls, sub_waves):
        """Generates successive sub-waves compatible with TowerGame.queue_wave
        
        Parameters:
            sub_waves: list of (steps, count, enemy_class, args, kwargs) tuples, where
                       parameters align with AbstractLevel.generate_sub_wave
        """
        enemies = []
        offset = 0
        for steps, count, enemy_class, args, kwargs in sub_waves:
            if count is not None:
                enemies.extend(cls.generate_sub_wave(steps, count, enemy_class,
                                                     args=args, kwargs=kwargs, offset=offset))

            offset += steps

        return enemies
