from enemy import SimpleEnemy
from range_ import CircularRange
from utilities import rectangles_intersect, get_delta_through_centre, \
    angle_between, rotate_toward
from tower import SimpleTower
import math


class CustomEnemy(SimpleEnemy):
    """custom type(energy) of enemy"""
    name = "Energy Enemy"
    colour = 'ORANGE'

    points = 10

    def __init__(self, grid_size=(.2, .2), grid_speed=5 / 60, health=100):
        super().__init__(grid_size, grid_speed, health)

    def damage(self, energy: int, type_: str):
        """Inflict damage on the enemy

        Parameters:
            energy(int): The amount of energy to inflict
            type_ (str): The type of damage to do
        """
        if type_ == "energy":
            self.health -= energy
            if self.health < 0:
                self.health = 0


class CustomTower(SimpleTower):
    """A custom tower with short range that rotates towards energy enemies."""
    name = 'Energy Tower'
    colour = '#FEC40a'

    range = CircularRange(1.5)
    cool_down_steps = 0

    base_cost = 40
    level_cost = 30

    rotation_threshold = (1 / 6) * math.pi

    def __init__(self, cell_size: int, grid_size=(.9, .9),
                 rotation=math.pi * .25,
                 base_damage=5, level: int = 1):
        super().__init__(cell_size, grid_size, rotation, base_damage, level)

    def step(self, data):
        """Rotates toward 'target' and attacks if possible"""
        self.cool_down.step()

        target = self.get_unit_in_range(data.enemies)

        if target is None:
            return

        # check if the enemy is custom enemy.
        for enemy in self.get_units_in_range(data.enemies):
            if not enemy.name == "Energy Enemy":
                return
            else:
                target = enemy
                break

        angle = angle_between(self.position, target.position)
        partial_angle = rotate_toward(self.rotation, angle,
                                      self.rotation_threshold)
        self.rotation = partial_angle

        # use energy to attack enemies.
        if partial_angle == angle:
            target.damage(self.get_damage(), 'energy')


class AdvancedTower(SimpleTower):
    """A tower that can slow down enemies"""
    name = 'Slow Tower'
    colour = 'BLUE'

    cool_down_steps = 10

    base_cost = 40
    level_cost = 30

    rotation_threshold = (1 / 3) * math.pi

    def __init__(self, cell_size: int, grid_size=(.9, .9),
                 rotation=math.pi * .25, base_damage=0, level: int = 1):
        super().__init__(cell_size, grid_size=grid_size, rotation=rotation,
                         base_damage=base_damage, level=level)

    def step(self, data):
        """Rotates toward 'target' and slow down it if possible"""
        self.cool_down.step()

        target = self.get_unit_in_range(data.enemies)

        if target is None:
            return

        angle = angle_between(self.position, target.position)
        partial_angle = rotate_toward(self.rotation, angle,
                                      self.rotation_threshold)
        self.rotation = partial_angle

        if angle != partial_angle or not self.cool_down.is_done():
            return None

        self.cool_down.start()

        # slow down the target.
        if partial_angle == angle:
            if target.grid_speed > 1 / 50:
                target.grid_speed -= 1 / 600


class AdvancedEnemy(SimpleEnemy):
    """Advanced Enemy"""
    name = "Advanced Enemy"
    colour = 'BLACK'

    points = 50

    def __init__(self, grid_size=(.2, .2), grid_speed=5 / 60, health=200,
                 stage=2):
        super().__init__(grid_size, grid_speed, health)
        self._stage = stage

    def _change_stage(self):
        """Control the different stage of enemy"""
        self.size = (30, 30)
        if self._stage == 1:
            self.colour = 'BROWN'
            self.size = (20, 20)
        elif self._stage == 0:
            self.colour = 'RED'
            self.size = (15, 15)

    def damage(self, damage, type_):
        """Inflict damage on the enemy

        Parameters:
            damage (int): The amount of damage to inflict
            type_ (str): The type of damage to do i.e. projectile, explosive
        """
        # every stage has 200 health.
        self.health -= damage
        if self.health < 0 and self._stage == 2:
            self.health = 200
            self._stage -= 1
        elif self.health < 0 and self._stage == 1:
            self.health = 200
            self._stage -= 1
        elif self._stage == 0 and self.health < 0:
            self.health = 0

    def step(self, data):
        """Move the enemy forward a single time-step

        Parameters:
            grid (GridCoordinateTranslator): Grid the enemy is currently on
            path (Path): The path the enemy is following

        Returns:
            bool: True iff the new location of the enemy is within the grid
        """
        grid = data.grid
        path = data.path

        # Update stages
        self._change_stage()

        # Repeatedly move toward next cell centre as much as possible
        movement = self.grid_speed
        while movement > 0:
            cell_offset = grid.pixel_to_cell_offset(self.position)

            # Assuming cell_offset is along an axis!
            offset_length = abs(cell_offset[0] + cell_offset[1])

            if offset_length == 0:
                partial_movement = movement
            else:
                partial_movement = min(offset_length, movement)

            cell_position = grid.pixel_to_cell(self.position)
            delta = path.get_best_delta(cell_position)

            # Ensures enemy will move to the centre before moving toward delta
            dx, dy = get_delta_through_centre(cell_offset, delta)

            speed = partial_movement * self.cell_size
            self.move_by((speed * dx, speed * dy))
            self.position = tuple(int(i) for i in self.position)

            movement -= partial_movement

        intersects = rectangles_intersect(*self.get_bounding_box(), (0, 0),
                                          grid.pixels)
        return intersects or grid.pixel_to_cell(self.position) in path.deltas
