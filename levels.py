import custom
from enemy import SimpleEnemy
from level import AbstractLevel


class MyLevel(AbstractLevel):
    """A simple game level containing examples of how to generate a wave"""
    waves = 20

    def get_wave(self, wave):
        """Returns enemies in the 'wave_n'th wave

        Parameters:
            wave_n (int): The nth wave

        Return:
            list[tuple[int, AbstractEnemy]]: A list of (step, enemy) pairs in the
                                             wave, sorted by step in ascending order
        """
        enemies = []

        if wave == 1:
            # A hardcoded singleton list of (step, enemy) pairs

            enemies = [(10, custom.AdvancedEnemy())]
        elif wave == 2:
            # A hardcoded list of multiple (step, enemy) pairs

            enemies = [(10, SimpleEnemy()), (15, SimpleEnemy()),
                       (30, custom.CustomEnemy())]
        elif 3 <= wave < 10:
            # List of (step, enemy) pairs spread across an interval of time (steps)

            steps = int(40 * (
                    wave ** .5))  # The number of steps to spread the enemies across
            count = wave * 2  # The number of enemies to spread across the (time) steps

            for step in self.generate_intervals(steps, count):
                enemies.append((step, SimpleEnemy()))

        elif wave == 10:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (50, 10, SimpleEnemy, (), {}),  # 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 10, SimpleEnemy, (), {})
                # then another 10 enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)

        else:  # 11 <= wave <= 20
            # Now it's going to get hectic

            sub_waves = [
                (
                    int(13 * wave),  # total steps
                    int(25 * wave ** (wave / 50)),  # number of enemies
                    SimpleEnemy,  # enemy constructor
                    (),  # positional arguments to provide to enemy constructor
                    {},  # keyword arguments to provide to enemy constructor
                ),
                # ...
            ]
            enemies = self.generate_sub_waves(sub_waves)

        return enemies


class IntermediateLevel(AbstractLevel):
    """The intermediate game level"""
    waves = 30

    def get_wave(self, wave):
        """Returns enemies in the 'wave_n'th wave

        Parameters:
            wave_n (int): The nth wave

        Return:
            list[tuple[int, AbstractEnemy]]: A list of (step, enemy) pairs in the
                                             wave, sorted by step in ascending order
        """
        enemies = []

        if wave == 1:
            # A hardcoded singleton list of (step, enemy) pairs

            enemies = [(10, custom.AdvancedEnemy())]
        elif wave == 2:
            # A hardcoded list of multiple (step, enemy) pairs

            enemies = [(10, custom.CustomEnemy()), (15, SimpleEnemy()),
                       (30, custom.CustomEnemy())]
        elif 3 <= wave < 10:
            # List of (step, enemy) pairs spread across an interval of time (steps)

            steps = int(40 * (
                    wave ** .5))  # The number of steps to spread the enemies across
            count = wave * 2  # The number of enemies to spread across the (time) steps
            counter = 0  # The counter to generate different enemies.

            for step in self.generate_intervals(steps, count):
                if counter % 2 == 0:
                    enemies.append((step, SimpleEnemy()))
                else:
                    enemies.append((step, custom.CustomEnemy()))
                counter += 1

        elif wave == 10:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (50, 10, SimpleEnemy, (), {}),  # 10 enemies over 50 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 10, custom.CustomEnemy, (), {})
                # then 10 energy enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)
        elif 10 < wave <= 20:
            # Now it's going to get hectic

            sub_waves = [
                (
                    int(13 * wave),  # total steps
                    int(25 * wave ** (wave / 50)),  # number of enemies
                    SimpleEnemy,  # enemy constructor
                    (),  # positional arguments to provide to enemy constructor
                    {},  # keyword arguments to provide to enemy constructor
                ),
                # ...
            ]
            enemies = self.generate_sub_waves(sub_waves)
        elif 20 < wave <= 30:  # All enemies are advanced enemies.
            # List of (step, enemy) pairs spread across an interval of time (steps)
            steps = int(80 * (
                    (wave-17) ** .5))  # The number of steps to spread the enemies across
            count = (wave-20)  # The number of enemies to spread across the (time) steps

            for step in self.generate_intervals(steps, count):
                enemies.append((step, custom.AdvancedEnemy()))

        return enemies


class AdvancedLevel(AbstractLevel):
    """The advanced game level"""
    waves = 30

    def get_wave(self, wave):
        """Returns enemies in the 'wave_n'th wave

        Parameters:
            wave_n (int): The nth wave

        Return:
            list[tuple[int, AbstractEnemy]]: A list of (step, enemy) pairs in the
                                             wave, sorted by step in ascending order
        """
        enemies = []

        if wave == 1:
            # A hardcoded singleton list of (step, enemy) pairs

            enemies = [(10, custom.AdvancedEnemy())]
        elif wave == 2:
            # A hardcoded list of multiple (step, enemy) pairs

            enemies = [(10, custom.CustomEnemy()), (15, SimpleEnemy()),
                       (30, custom.CustomEnemy())]
        elif 3 <= wave < 10:
            # List of (step, enemy) pairs spread across an interval of time (steps)

            steps = int(40 * (
                    wave ** .5))  # The number of steps to spread the enemies across
            count = wave * 2  # The number of enemies to spread across the (time) steps
            counter = 0  # The counter to generate different enemies.

            for step in self.generate_intervals(steps, count):
                if counter % 2 == 0:
                    enemies.append((step, SimpleEnemy()))
                else:
                    enemies.append((step, custom.CustomEnemy()))
                counter += 1

        elif wave == 10:
            # Generate sub waves
            sub_waves = [
                # (steps, number of enemies, enemy constructor, args, kwargs)
                (150, 5, custom.AdvancedEnemy, (), {}),  # 5 advanced enemies over 150 steps
                (100, None, None, None, None),  # then nothing for 100 steps
                (50, 10, custom.CustomEnemy, (), {})
                # then 10 energy enemies over 50 steps
            ]

            enemies = self.generate_sub_waves(sub_waves)
        elif 10 < wave <= 20:
            # Now it's going to get hectic

            sub_waves = [
                (
                    int(13 * wave),  # total steps
                    int(25 * wave ** (wave / 50)),  # number of enemies
                    SimpleEnemy,  # enemy constructor
                    (),  # positional arguments to provide to enemy constructor
                    {},  # keyword arguments to provide to enemy constructor
                ),
                # ...
            ]
            enemies = self.generate_sub_waves(sub_waves)
        elif 20 < wave <= 30:  # Creates all types enemy for each wave.
            # List of (step, enemy) pairs spread across an interval of time (steps)
            steps = int(120 * (
                    (wave-17) ** .5))  # The number of steps to spread the enemies across
            count = (wave-20)  # The number of enemies to spread across the (time) steps

            for step in self.generate_intervals(steps, count):
                enemies.append((step, custom.AdvancedEnemy()))
                enemies.append(((step + 15), custom.CustomEnemy()))
                enemies.append(((step + 20), custom.CustomEnemy()))
                enemies.append(((step + 25), SimpleEnemy()))
                enemies.append(((step + 30), SimpleEnemy()))

        return enemies