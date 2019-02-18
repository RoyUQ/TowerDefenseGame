"""GUI Elements for a Tower Defence game"""

import tkinter as tk

from advanced_view import TowerView, RangeView, EnemyView, ObstacleView

__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2018, The University of Queensland"
__license__ = "MIT"
__version__ = "1.1.0"


class GameView(tk.Canvas):
    """Game view which displays the user interface for the Towers game"""

    def __init__(self, master, *args, size=(6, 6), cell_size=40,
                 tower_view_class=TowerView, range_view_class=RangeView,
                 enemy_view_class=EnemyView, obstacle_view_class=ObstacleView,
                 **kwargs):
        """
        Constructs a GameView inside the tkinter master widget

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget
            size (tuple<int, int>): The (row, column) size of the grid
            cell_size (int): The size of each cell in the game, in pixels
            tower_view_class (Class<TowerView>): The class to draw towers
            range_view_class (Class<RangeView>): The class to draw ranges  
            enemy_view_class (Class<EnemyView>): The class to draw enemies
            obstacle_view_class (Class<ObstacleView>): The class to draw obstacles
            **kwargs: Any other keyword arguments for the Canvas constructor
        """

        self.size = size
        self.cell_size = cell_size

        self.width, self.height = width, height = tuple(i * self.cell_size
                                                        for i in self.size)

        tk.Canvas.__init__(self, master, *args, width=width, height=height,
                           highlightthickness=0, **kwargs)

        self.tower_view_class = tower_view_class
        self.range_view_class = range_view_class
        self.enemy_view_class = enemy_view_class
        self.obstacle_view_class = obstacle_view_class

    def draw_borders(self, borders, fill='old lace'):
        """
        Draws the border lines of the game view, after first removing any existing

        Parameters:
            borders (iter<tuple<int, int>,
                          tuple<int, int>>): A series of pixel positions for
                                             laying out the borders of the view.
            fill (str): The colour of the borders to draw
        """
        self.delete('border')
        for start, end in borders:
            self.create_line(start, end, fill=fill, tag='border')

    def draw_enemies(self, enemies):
        """
        Draws all enemies, after first removing any existing

        Parameters:
            enemies (list<AbstractEnemy>): A list of enemies to draw to the view.
        """
        self.delete('enemy')
        for enemy in enemies:
            self.enemy_view_class.draw(self, enemy)

    def draw_towers(self, towers):
        """
        Draws all towers, after first removing any existing

        Parameters:
            towers (dict{tuple(int, int), AbstractTower}):
                Towers to draw to the view.
                dict contains a mapping of cell position to tower.
        """
        self.delete('tower')
        for tower in towers.values():
            self.tower_view_class.draw(self, tower)

        self.tag_raise('shadow')

    def draw_obstacles(self, obstacles):
        """
        Draws all obstacles, after first removing any existing

        Parameters:
            obstacles (list<Unit>): A list of obstacles to draw to the view.
        """
        self.delete('obstacle')
        for obstacle in obstacles:
            self.obstacle_view_class.draw(self, obstacle)

    def draw_path(self, coordinates):
        """
        Draws a path on the game view, after first removing any existing
        Useful to preview where the enemies will travel after placing a tower.
        
        Parameters:
            coordinates (list[tuple[int, int]]): A list of (x, y) coordinate pairs.
        """

        self.delete('path')
        tag = self.create_line(coordinates, tag='path', dash=(2, 4))
        self.tag_lower(tag)
        self.tag_lower('border')

    def draw_preview(self, tower, legal=True):
        """
        Draws a preview of a tower over the game view, after first removing any existing
        Used for visual aid when placing a tower

        Parameter:
            tower (AbstractTower|None): The preview tower or None if no tower
                                        should be drawn
        """
        self.delete("shadow", "range")

        if tower is None:
            return

        # draw a preview tower for placement
        if legal:
            # range
            tags = self.range_view_class.draw(self, tower.range, tower.position,
                                              tower.cell_size)
            for tag in tags:
                self.itemconfig(tag, outline='green')
                self.addtag_withtag('shadow', tag)

            # tower
            tags = self.tower_view_class.draw(self, tower)
            for tag in tags:
                self.addtag_withtag('shadow', tag)
                self.dtag(tag, 'tower')
        else:
            top_left, bottom_right = tower.get_bounding_box()

            left, top = top_left
            right, bottom = bottom_right

            self.create_line(top_left, bottom_right, tag='shadow', fill='black')
            self.create_line((right, top), (left, bottom), tag='shadow', fill='black')
