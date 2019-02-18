"""Contains view logic for towers & ranges

Ideally, there would be a view class for each unit (tower/range/enemy), inheriting from a super 
class (i.e. AbstractTowerView) with a more complicated file structure. However, for simplicity's
sake, this has been avoided in favour of a single view class with methods for each kind of unit.

If you wish to add additional types of visuals for units, simply inherit from the appropriate class
and set the corresponding keyword argument in view.GameView
"""

#
#                         /-------------\
#                        /               \
#                       /                 \
#                      /                   \
#                      |   XXXX     XXXX   |
#                      |   XXXX     XXXX   |
#                      |   XXX       XXX   |
#                      \         X         /
#                       --\     XXX     /--
#                        | |    XXX    | |
#                        | |           | |
#                        | I I I I I I I |
#                        |  I I I I I I  |
#                         \              /
#                           --         --
#                             \-------/
#                     XXX                    XXX
#                   XXXXX                  XXXXX
#                   XXXXXXXXX         XXXXXXXXXX
#                           XXXXX   XXXXX
#                             XXXXXXX
#                           XXXXX   XXXXX
#                   XXXXXXXXX         XXXXXXXXXX
#                   XXXXX                  XXXXX
#                     XXX                    XXX
#                           **************
#                           *  BEWARE!!  *
#                           **************
#                       All ye who enter here:
#                  Most of the code in this module
#                      is twisted beyond belief!
#                         Tread carefully
#                  If you think you understand it,
#                             You Don't,
#                           So Look Again
#

import math
import tkinter as tk

from range_ import AbstractRange, DonutRange, PlusRange, CircularRange
from tower import AbstractTower, MissileTower, PulseTower, SimpleTower, \
    AbstractObstacle, Missile, Pulse
from enemy import AbstractEnemy
from utilities import rotate_point

__author__ = "Benjamin Martin"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"


def sort_draw_methods(draw_methods):
    """Returns a sorted copy, with child classes preceding their parents"""

    # Any child class must logically have a method resolution order longer
    # than any of its parents, so reverse sort by method resolution order
    return sorted(draw_methods, key=lambda i: len(i[0].mro()), reverse=True)


class SimpleView:
    """Single class to manage drawing instances of a variety of (sub)classes on a canvas"""
    draw_methods = sort_draw_methods([])  # list of (class, draw_method) pairs

    @classmethod
    def get_draw_method(cls, instance):
        """(Callable) Returns the draw method for instance
        
        Draw method is determined by finding first class that instance is an instance of"""

        method = None

        for key, method_name in cls.draw_methods:
            if isinstance(instance, key) or instance == key:
                method = getattr(cls, method_name)
                break

        if method is None:
            raise KeyError(f"Unable to find draw method for {instance}")

        return method


class RangeView(SimpleView):
    """Manages view logic for ranges"""
    # Sorting ensures child classes are given higher precedence than their parent classes
    draw_methods = sort_draw_methods([
        (CircularRange, '_draw_circular'),
        (DonutRange, '_draw_donut'),
        (PlusRange, '_draw_plus')
    ])

    @classmethod
    def draw(cls, canvas: tk.Canvas, range_: AbstractRange, position, cell_size, *args, **kwargs):
        """Draws a 'range_' on a 'canvas'
        
        Parameters:
            canvas (tk.Canvas): The canvas to draw on
            range_ (AbstractRange): The range to draw
            position (tuple<int, int>): The (x, y) position to centre the drawing on
            cell_size (int): The size of a drawing cell
            *args: Extra position arguments to pass to the draw method
            **kwargs: Extra keyword arguments to pass to the draw method
        """
        return cls.get_draw_method(range_)(canvas, range_, position, cell_size, *args, **kwargs)

    @classmethod
    def _draw_circular(cls, canvas: tk.Canvas, range_: CircularRange, position, cell_size):
        """Draws a circular range"""
        x, y = position
        dr = range_.radius * cell_size
        return [canvas.create_oval(x - dr, y - dr, x + dr, y + dr, tag='range')]

    @classmethod
    def _draw_donut(cls, canvas: tk.Canvas, range_: DonutRange, position, cell_size):
        """Draws a donut range"""
        tags = []
        x, y = position
        for radius in (range_.inner_radius, range_.outer_radius):
            dr = radius * cell_size
            tag = canvas.create_oval(x - dr, y - dr, x + dr, y + dr, tag='range')
            tags.append(tag)
        return tags

    @classmethod
    def _draw_plus(cls, canvas: tk.Canvas, range_: PlusRange, position, cell_size):
        """Draws a plus range"""
        x, y = position
        # pylint: disable=invalid-name
        o = range_.outer_radius * cell_size
        i = range_.inner_radius * cell_size

        # Could derive a formula, but cbf
        coords = [
            (-o, i), (-i, i), (-i, o),
            (i, o), (i, i), (o, i),
            (o, -i), (i, -i), (i, -o),
            (-i, -o), (-i, -i), (-o, -i)
        ]

        coords.append(coords[0])

        coords = [(x + dx, y + dy) for dx, dy in coords]

        return [canvas.create_polygon(coords, tag='range', fill='')]


class TowerView(SimpleView):
    """Manages view logic for towers"""
    # Sorting ensures child classes are given higher precedence than their parent classes
    draw_methods = sort_draw_methods([
        (SimpleTower, '_draw_simple'),
        (MissileTower, '_draw_missile'),
        (PulseTower, '_draw_pulse'),
        (AbstractTower, '_draw_simple'),
    ])

    @classmethod
    def draw(cls, canvas: tk.Canvas, tower: AbstractTower, *args, **kwargs):
        """Draws a 'tower' on a 'canvas', centred at its position

        Parameters:
            canvas (tk.Canvas): The canvas to draw on
            tower (AbstractTower): The tower to draw
            *args: Extra position arguments to pass to the draw method
            **kwargs: Extra keyword arguments to pass to the draw method
        """
        return cls.get_draw_method(tower)(canvas, tower, *args, **kwargs)

    @classmethod
    def _draw_simple(cls, canvas: tk.Canvas, tower_: SimpleTower):
        """Draws a simple tower"""

        x, y = tower_.position
        angle = tower_.rotation

        x_diameter, y_diameter = tower_.grid_size
        top_left, bottom_right = tower_.get_bounding_box()

        cell_size = tower_.cell_size

        colour = tower_.colour

        return [canvas.create_oval(top_left, bottom_right, tag='tower', fill=colour),
                canvas.create_line(x, y, x + (x_diameter / 2) * cell_size * math.cos(angle),
                                   y + (y_diameter / 2) * cell_size * math.sin(angle),
                                   tag='tower')]

    @classmethod
    def _draw_pulse(cls, canvas: tk.Canvas, tower_: SimpleTower):
        """Draws a pulse tower"""

        x, y = tower_.position

        x_diameter, y_diameter = tower_.grid_size
        top_left, bottom_right = tower_.get_bounding_box()

        cell_size = tower_.cell_size

        colour = tower_.colour

        body = canvas.create_oval(top_left, bottom_right, tag='tower', fill=colour)
        tags = [body]

        angle_step = math.pi/2
        for i in range(4):
            angle = i * angle_step

            dx = (x_diameter / 2) * cell_size * math.cos(angle)
            dy = (y_diameter / 2) * cell_size * math.sin(angle)

            tag = canvas.create_line(x + dx/2, y + dy/2, x + dx, y + dy, tag='tower')

            tags.append(tag)



        return tags

    @classmethod
    def _draw_missile(cls, canvas: tk.Canvas, tower_: MissileTower):
        """Draws a missile tower"""

        x, y = tower_.position
        angle = tower_.rotation

        x_diameter, y_diameter = tower_.grid_size
        top_left, bottom_right = tower_.get_bounding_box()

        cell_size = tower_.cell_size

        colour = tower_.colour

        body = canvas.create_oval(top_left, bottom_right, tag='tower', fill=colour)

        tags = [body]

        for delta_angle in (-math.pi/12, math.pi/12):
            tags.append(
                canvas.create_line(x, y, x + (x_diameter / 2) * cell_size * math.cos(angle + delta_angle),
                                   y + (y_diameter / 2) * cell_size * math.sin(angle + delta_angle),
                                   tag='tower')
            )

        return tags


class EnemyView(SimpleView):
    """Manages view logic for enemies"""
    # Sorting ensures child classes are given higher precedence than their parent classes
    draw_methods = sort_draw_methods([
        (AbstractEnemy, '_draw_simple'),
    ])

    @classmethod
    def draw(cls, canvas: tk.Canvas, enemy: AbstractEnemy, *args, **kwargs):
        """Draws a 'enemy' on a 'canvas', centred at its position

        Parameters:
            canvas (tk.Canvas): The canvas to draw on
            enemy (AbstractEnemy): The enemy to draw
            *args: Extra position arguments to pass to the draw method
            **kwargs: Extra keyword arguments to pass to the draw method
        """
        return cls.get_draw_method(enemy)(canvas, enemy, *args, **kwargs)

    @classmethod
    def _draw_simple(cls, canvas: tk.Canvas, enemy: AbstractEnemy):
        """Draws an enemy"""

        top_left, bottom_right = enemy.get_bounding_box()

        # create
        outline = canvas.create_oval(top_left, bottom_right, tags='enemy',
                                     fill='white smoke')
        extent = enemy.percentage_health() * 360
        if extent == 360:  # because tkinter is lame
            extent = 359.9999

        fill = canvas.create_arc(top_left, bottom_right, tags='enemy',
                                 fill=enemy.colour, start=45, extent=-extent,
                                 outline='')

        return [outline, fill]


class ObstacleView(SimpleView):
    """Manages view logic for obstacles"""
    # Sorting ensures child classes are given higher precedence than their parent classes
    draw_methods = sort_draw_methods([
        (AbstractObstacle, '_draw_invisible'),
        (Missile, '_draw_missile'),
        (Pulse, '_draw_pulse')
    ])

    @classmethod
    def draw(cls, canvas: tk.Canvas, obstacle: AbstractObstacle, *args, **kwargs):
        """Draws an 'obstacle' on a 'canvas', centred at its position

        Parameters:
            canvas (tk.Canvas): The canvas to draw on
            obstacle (AbstractObstacle): The obstacle to draw
            *args: Extra position arguments to pass to the draw method
            **kwargs: Extra keyword arguments to pass to the draw method
        """
        return cls.get_draw_method(obstacle)(canvas, obstacle, *args, **kwargs)

    @classmethod
    def _draw_invisible(cls, canvas: tk.Canvas, obstacle: AbstractObstacle):
        """Draws an invisible obstacle"""

    @classmethod
    def _draw_missile(cls, canvas: tk.Canvas, missile: Missile):
        """Draws a missile"""

        x, y = missile.position

        length, width = missile.size

        dx, dy = rotate_point((length / 2, width / 2), missile.rotation)

        head = x + dx, y + dy
        tail = x - dx, y - dy

        return canvas.create_line(head, tail, tag='obstacle')

    @classmethod
    def _draw_pulse(cls, canvas: tk.Canvas, pulse: Pulse):
        """Draws a pulse"""

        x, y = pulse.position
        radius = pulse.size[0]

        head = x + radius, y + radius
        tail = x - radius, y - radius

        return canvas.create_oval(head, tail, fill=pulse.colour, tag='obstacle')
