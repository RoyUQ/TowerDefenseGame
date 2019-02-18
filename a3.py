import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import custom
import math
import high_score_manager
from advanced_view import TowerView
from model import TowerGame
from tower import SimpleTower, MissileTower, PulseTower, AbstractTower
from enemy import SimpleEnemy
from utilities import Stepper
from view import GameView
from level import AbstractLevel
from levels import MyLevel, IntermediateLevel, AdvancedLevel

BACKGROUND_COLOUR = "#4a2f48"

__author__ = ""
__copyright__ = ""
"""The introduction of independent research is in pdf file."""


class TowerGameApp(Stepper):
    """Top-level GUI application for a simple tower defence game"""

    # All private attributes for ease of reading
    _current_tower = None
    _paused = False
    _won = None

    _level = None
    _wave = None
    _score = None
    _coins = None
    _lives = None

    _master = None
    _game = None
    _view = None

    def __init__(self, master: tk.Tk, delay: int = 20):
        """Construct a tower defence game in a root window

        Parameters:
            master (tk.Tk): Window to place the game into
        """

        self._master = master
        master.title("Towers")
        super().__init__(master, delay=delay)

        self._game = game = TowerGame()

        self.setup_menu()

        # setup the HighScoreManager to process records.
        self._score_manager = high_score_manager.HighScoreManager()

        # create a game view and draw grid borders
        self._view = GameView(master, size=game.grid.cells,
                              cell_size=game.grid.cell_size,
                              bg='antique white')
        self._view.pack(side=tk.LEFT, expand=True)

        # Task 1.3 (Status Bar): instantiate status bar
        self._status_bar = StatusBar(master, bg='white', width=80, height=16)
        self._status_bar.pack(side=tk.TOP, fill=tk.X)

        # Task 1.5 (Play Controls): instantiate widgets here
        self._control_frame = tk.Frame(master, bg="#4B2E49")
        self._control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self._frame1 = tk.Frame(self._control_frame)
        self._frame1.pack(anchor=tk.CENTER)

        self._button1 = tk.Button(self._frame1, text='Next Wave',
                                  state=tk.NORMAL,
                                  command=self.next_wave)
        self._button1.pack(side=tk.LEFT, padx=1, pady=1)
        self._button2 = tk.Button(self._frame1, text='Play', state=tk.NORMAL,
                                  command=self._toggle_paused)
        self._button2.pack(side=tk.LEFT, padx=1, pady=1)

        # A frame for checkbox and it will be created by _show_checkbox method.
        self._frame2 = tk.Frame(self._control_frame)

        # bind game events
        game.on("enemy_death", self._handle_death)
        game.on("enemy_escape", self._handle_escape)
        game.on("cleared", self._handle_wave_clear)

        # Task 1.2 (Tower Placement): bind mouse events to canvas here
        self._view.bind("<Button-1>", self._left_click)
        self._view.bind("<Motion>", self._move)
        self._view.bind("<Leave>", self._mouse_leave)
        self._view.bind("<Button-3>", self._right_click)

        # instantiate shop bar
        self._shop = tk.Frame(master, bg='#4B2E49')
        self._shop.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        towers = [
            SimpleTower,
            MissileTower,
            custom.CustomTower,
            custom.AdvancedTower
        ]
        self._tower_views = []

        # Create views for each tower & store to update if availability changes
        for tower_class in towers:
            tower = tower_class(self._game.grid.cell_size // 2)
            tower_view = ShopTowerView(self._shop, tower,
                                       click_command=lambda class_=tower_class:
                                       self.select_tower(class_),
                                       bg="#4B2E49")

            tower_view.pack(fill=tk.X)
            self._tower_views.append((tower, tower_view))

        # Level
        self._level = MyLevel()

        self.select_tower(SimpleTower)

        self._view.draw_borders(game.grid.get_border_coordinates())

        # Get ready for the game
        self._setup_game()

        # Remove the relevant lines while attempting the corresponding section
        # Hint: Comment them out to keep for reference

        # Task 1.2 (Tower Placement): remove these lines
        # towers = [
        #     ([(2, 2), (3, 0), (4, 1), (4, 2), (4, 3)], SimpleTower),
        #     ([(2, 5)], MissileTower)
        # ]
        #
        # for positions, tower in towers:
        #     for position in positions:
        #         game.place(position, tower_type=tower)

        # Task 1.5 (Tower Placement): remove these lines
        # game.queue_wave([], clear=True)
        # self._wave = 4 - 1  # first (next) wave will be wave 4
        # self.next_wave()

        # Task 1.5 (Play Controls): remove this line
        # self.start()

    def _toggle_paused(self, paused=None):
        """Toggles or sets the paused state

        Parameters:
            paused (bool): Toggles/pauses/unpauses if None/True/False, respectively
        """
        if paused is None:
            paused = not self._paused

        # Task 1.5 (Play Controls): Reconfigure the pause button here

        if paused:
            self.pause()
            self._button2.config(text="Play")
        else:
            self.start()
            self._button2.config(text="Pause")

        self._paused = paused

    def _setup_game(self):
        """Sets up the game"""
        self._wave = 0
        self._score = 0
        self._coins = 200
        self._lives = 100

        self._won = False

        # Task 1.3 (Status Bar): Update status here
        self._status_bar.waves_update(self._wave, self._level.get_max_wave())
        self._status_bar.score_update(self._score)
        self._status_bar.coin_update(self._coins)
        self._status_bar.life_update(self._lives)

        # Task 1.5 (Play Controls): Re-enable the play controls here (if they were ever disabled)
        self._button1.configure(state=tk.NORMAL)
        self._button2.configure(state=tk.NORMAL)
        self._game.reset()

        # Auto-start the first wave
        self.next_wave()
        self._toggle_paused(paused=True)

        # display each of the available towers
        self._available_towers()
        # destroy checkbox if it exist.
        self._frame2.destroy()

    def _available_towers(self):
        """display each of the available towers"""
        for tower in self._tower_views:
            if self._coins < tower[0].get_value():
                tower[1].red_text(False)
            else:
                tower[1].red_text(True)

    # Task 1.4 (File Menu): Complete menu item handlers here (including docstrings!)
    def setup_menu(self):
        """Sets up the application menu"""
        # Task 1.4: construct file menu here
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)
        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New Game", command=self._new_game)
        filemenu.add_command(label="Exit", command=self._exit)
        filemenu.add_command(label="HighScores", command=self._display)
        filemenu.add_command(label="Simple level",
                             command=lambda: self._change_level(1))
        filemenu.add_command(label="Intermediate level",
                             command=lambda: self._change_level(2))
        filemenu.add_command(label="Advanced level",
                             command=lambda: self._change_level(3))

    def _change_level(self, level):
        """Change the current game level.

        Parameters:
            level (int): the game level
        """
        if level == 1:
            self._level = MyLevel()
            for tower in self._tower_views:
                tower[0].level = 1
                tower[1].update_price()
            self._new_game()
        elif level == 2:
            self._level = IntermediateLevel()
            # change the level of each tower.
            for tower in self._tower_views:
                tower[0].level = 2
                tower[1].update_price()
            self._new_game()
        elif level == 3:
            self._level = AdvancedLevel()
            # change the level of each tower.
            for tower in self._tower_views:
                tower[0].level = 3
                tower[1].update_price()
            self._new_game()

    def _new_game(self):
        """Start a new game"""
        self._setup_game()
        self.refresh_view()

    def _exit(self):
        """Exit the current game"""
        if messagebox.askokcancel("EXIT", "Do you want to exit?"):
            self._master.destroy()

    def _display(self):
        """Creates a window to displays the names and
        scores of the top ten scoring players"""
        window = tk.Toplevel()
        window.minsize(height=200, width=400)
        window.title("High Scores")
        records = ""
        for record in self._score_manager.get_entries():
            # Oder the records from top to bottom.
            records = records + "Name: {},   Score: {},   Data: {}\n".format(
                record['name'],
                record['score'], record['data'])
        label = tk.Label(window, text=records).pack()
        window.mainloop()

    def _show_checkbox(self, tower):
        """Show the checkbox when a player left-clicks on a tower in the grid

        Parameters:
            tower (AbstractTower): the current tower
        """
        # Creates a frame for checkbox.
        self._frame2 = tk.Frame(self._control_frame)
        self._frame2.pack(side=tk.BOTTOM, anchor=tk.CENTER)

        label = tk.Label(self._frame2, text="Upgrade Tower:").pack(side=tk.TOP,
                                                                   fill=tk.X)

        # upgrade damage of SimpleTower or EnergyTower.
        if not (isinstance(tower, MissileTower) or isinstance(tower,
                                                              custom.AdvancedTower)):
            var1 = tk.IntVar()
            button5 = tk.Checkbutton(self._frame2,
                                     text="increase damage: 10 coins",
                                     variable=var1).pack(side=tk.LEFT)
            button6 = tk.Button(self._frame2, text='submit', state=tk.NORMAL,
                                command=lambda: self._update_damage(var1.get(),
                                                                    tower)).pack(
                side=tk.LEFT)

        # upgrade cool down time of MissileTower or SlowTower.
        if isinstance(tower, MissileTower) or isinstance(tower,
                                                         custom.AdvancedTower):
            var2 = tk.IntVar()
            button7 = tk.Checkbutton(self._frame2,
                                     text="reduce cool down time: 10 coins",
                                     variable=var2).pack(side=tk.LEFT)
            button8 = tk.Button(self._frame2, text='submit', state=tk.NORMAL,
                                command=lambda: self._update_cool_time(
                                    var2.get(), tower)).pack(side=tk.LEFT)

    def _update_damage(self, var, tower):
        """Update the damage of selected tower.

        Parameters:
            var (int): the value of Checkbutton
            tower (AbstractTower): the selected tower
        """
        if var == 1:
            # print(111)
            tower.base_damage = tower.base_damage + 5
            self._coins = self._coins - 10
            self.refresh_view()
            self._available_towers()
            self._frame2.destroy()
        elif var == 0:
            self._frame2.destroy()

    def _update_cool_time(self, var, tower):
        """Update the cool down time of selected tower.

        Parameters:
            var (int): the value of Checkbutton
            tower (AbstractTower): the selected tower
        """

        if var == 1 and tower.cool_down_steps > 2:
            tower.cool_down_steps = tower.cool_down_steps - 2
            self._coins = self._coins - 10
            self.refresh_view()
            self._available_towers()
            self._frame2.destroy()
        elif tower.cool_down_steps <= 2:
            messagebox.showinfo("Message",
                                "cool down time is already the minimum")
            self._frame2.destroy()
        elif var == 0:
            self._frame2.destroy()

    def refresh_view(self):
        """Refreshes the game view"""
        if self._step_number % 2 == 0:
            self._view.draw_enemies(self._game.enemies)
        self._view.draw_towers(self._game.towers)
        self._view.draw_obstacles(self._game.obstacles)

    def _step(self):
        """
        Perform a step every interval

        Triggers a game step and updates the view

        Returns:
            (bool) True if the game is still running
        """
        self._game.step()
        self.refresh_view()

        return not self._won

    # Task 1.2 (Tower Placement): Complete event handlers here (including
    # docstrings!) Event handlers: _move, _mouse_leave, _left_click
    def _right_click(self, event):
        """
        Handles the mouse right click to remove the current tower.

        Parameter:
            event (tk.Event): Tkinter mouse event
        """
        position = event.x, event.y
        cell_position = self._game.grid.pixel_to_cell(position)
        self._coins = self._coins + self._game.towers.get(
            cell_position).get_value() * 0.8
        self._game.remove(cell_position)
        # display each of the available towers
        self._available_towers()

    def _move(self, event):
        """
        Handles the mouse moving over the game view canvas

        Parameter:
            event (tk.Event): Tkinter mouse event
        """
        if self._current_tower.get_value() > self._coins:
            return

        # move the shadow tower to mouse position
        position = event.x, event.y
        self._current_tower.position = position

        legal, grid_path = self._game.attempt_placement(position)

        # find the best path and covert positions to pixel positions
        path = [self._game.grid.cell_to_pixel_centre(position)
                for position in grid_path.get_shortest()]

        # Task 1.2 (Tower placement): Draw the tower preview here
        self._view.draw_preview(self._current_tower, legal)
        self._view.draw_path(path)

    def _mouse_leave(self, event):
        """"
        Handles the mouse left click to place the current tower.

        Parameter:
            event (tk.Event): Tkinter mouse event
        """

        # Task 1.2 (Tower placement): Delete the preview
        # Hint: Relevant canvas items are tagged with: 'path', 'range', 'shadow'
        #       See tk.Canvas.delete (delete all with tag)
        self._view.delete('path', 'range', 'shadow')

    def _left_click(self, event):
        """"
        Handles the mouse left click to place the current tower
        or active the checkbox.

        Parameter:
            event (tk.Event): Tkinter mouse event
        """
        # retrieve position to place tower
        if self._current_tower is None:
            return
        if self._coins < self._current_tower.get_value():
            return

        position = event.x, event.y
        cell_position = self._game.grid.pixel_to_cell(position)

        if self._game.place(cell_position,
                            tower_type=self._current_tower.__class__):
            # Task 1.2 (Tower Placement): Attempt to place the tower being previewed
            self._coins = self._coins - self._current_tower.get_value()
            # Store the initialized wave to the tower which we bought.
            self._game.towers.get(cell_position).my_wave = self._wave
            self.refresh_view()
            # display each of the available towers
            self._available_towers()
        else:
            # show the checkBox for the selected tower.
            tower = self._game.towers.get(cell_position)
            if tower.base_cost == 0:  # aging tower cannot be upgrade.
                self._frame2.destroy()
                return
            self._frame2.destroy()
            self._show_checkbox(tower)

    def next_wave(self):
        """Sends the next wave of enemies against the player"""
        if self._wave == self._level.get_max_wave():
            return

        self._wave += 1

        # In intermediate game level, the maximum age of tower is 15 waves.
        # In advanced game level, the maximum age of tower is 10 waves.
        if isinstance(self._level, IntermediateLevel):
            for tower in self._game.towers.values():
                if self._wave - tower.my_wave > 14:
                    tower.tower_aging()
        elif isinstance(self._level, AdvancedLevel):
            for tower in self._game.towers.values():
                if self._wave - tower.my_wave > 9:
                    tower.tower_aging()
        self.refresh_view()

        # Task 1.3 (Status Bar): Update the current wave display here
        self._status_bar.waves_update(self._wave, self._level.get_max_wave())

        # Task 1.5 (Play Controls): Disable the add wave button here (if this is the last wave)
        if self._wave == self._level.get_max_wave():
            self._button1.configure(state=tk.DISABLED)

        # Generate wave and enqueue
        wave = self._level.get_wave(self._wave)
        for step, enemy in wave:
            enemy.set_cell_size(self._game.grid.cell_size)

        self._game.queue_wave(wave)

    def select_tower(self, tower):
        """
        Set 'tower' as the current tower

        Parameters:
            tower (AbstractTower): The new tower type
        """
        self._current_tower = tower(self._game.grid.cell_size)

    def _handle_death(self, enemies):
        """
        Handles enemies dying

        Parameters:
            enemies (list<AbstractEnemy>): The enemies which died in a step
        """
        bonus = len(enemies) ** .5
        for enemy in enemies:
            self._coins += enemy.points
            self._score += int(enemy.points * bonus)

        # Task 1.3 (Status Bar): Update coins & score displays here
        self._status_bar.score_update(self._score)
        self._status_bar.coin_update(self._coins)

        # display each of the available towers
        self._available_towers()

    def _handle_escape(self, enemies):
        """
        Handles enemies escaping (not being killed before moving through the grid

        Parameters:
            enemies (list<AbstractEnemy>): The enemies which escaped in a step
        """
        self._lives -= len(enemies)
        if self._lives < 0:
            self._lives = 0

        # Task 1.3 (Status Bar): Update lives display here
        self._status_bar.life_update(self._lives)

        # Handle game over
        if self._lives == 0:
            self._handle_game_over(won=False)

    def _handle_wave_clear(self):
        """Handles an entire wave being cleared (all enemies killed)"""
        if self._wave == self._level.get_max_wave():
            self._handle_game_over(won=True)

        # Task 1.5 (Play Controls): remove this line
        # self.next_wave()

    def _handle_game_over(self, won=False):
        """Handles game over

        Parameter:
            won (bool): If True, signals the game was won (otherwise lost)
        """
        self._won = won
        self.stop()

        # Task 1.4 (Dialogs): show game over dialog here
        self._button1.configure(state=tk.DISABLED)
        self._button2.configure(state=tk.DISABLED)
        if self._won:
            messagebox.showinfo("Message", "You won!")
            self._high_score_prompt()
        if self._lives == 0:
            messagebox.showinfo("Message", "Game over!")
            self._high_score_prompt()

    def _high_score_prompt(self):
        """Check if score is enough to get in the high scores list"""
        if self._score_manager.does_score_qualify(self._score):
            prompt = tk.simpledialog.askstring("Input",
                                               "What is your name?")
            # Add a new record into the high scores list.
            self._score_manager.add_entry(prompt, self._score)


class StatusBar(tk.Frame):
    """A Bar show the basic information
    about user's status in the current game
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # creates a Label to show current wave and maximum wave.
        self._waves_value = tk.Label(self, text="Wave: Default", bg='white')
        self._waves_value.pack(side=tk.TOP)

        # creates a Label to show current score.
        self._score_value = tk.Label(self, text="Score: Default", bg='white')
        self._score_value.pack(side=tk.TOP)

        # information of coins
        self._image_coin = tk.PhotoImage(file="images/coins.gif")
        self._coin_value = tk.Label(self, image=self._image_coin, text="coins",
                                    bg='white', compound="left")
        self._coin_value.pack(side=tk.LEFT)

        # information of lives
        self._image_heart = tk.PhotoImage(file="images/heart.gif")
        self._life_value = tk.Label(self, image=self._image_heart, text="lives",
                                    bg='white', compound="left")
        self._life_value.pack(side=tk.LEFT, padx=80)

    def waves_update(self, wave_value, max_wave):
        """Update the waves when user click the 'next wave' button"""
        self._waves_value.configure(
            text="Wave: {}/{}".format(wave_value, max_wave))

    def score_update(self, score_value):
        """Update current score when the user gets score"""
        self._score_value.configure(text="{}".format(score_value))

    def coin_update(self, coin_value):
        """Update current coins when the user gains coins or lose coins"""
        self._coin_value.configure(text="{} coins".format(coin_value))

    def life_update(self, life_value):
        """Update current lives when the user is attacked by enemy"""
        self._life_value.configure(text="{} lives".format(life_value))


class ShopTowerView(tk.Frame):
    """A shop allows the user to select different towers."""

    def __init__(self, master, tower, click_command, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.bind("<Button-1>", self.choose_tower)

        # The frame for price and name of a tower
        self._bind = tk.Frame(self, bg='#4B2E49')
        self._bind.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self._bind.bind("<Button-1>", self.choose_tower)

        # setup canvas
        self._canvas = tk.Canvas(self._bind, bg='#4B2E49', highlightthickness=0,
                                 width=30, height=30)
        self._canvas.pack(side=tk.LEFT)
        self._canvas.bind("<Button-1>", self.choose_tower)

        # draw tower
        # Position in centre
        tower.position = (tower.cell_size // 2, tower.cell_size // 2)
        tower.rotation = 3 * math.pi / 2  # Point up
        TowerView.draw(self._canvas, tower)
        self.click_command = click_command

        # draw tower name
        self._tower_name = tk.Label(self._bind, text="{0}".format(tower.name),
                                    bg='#4B2E49', fg="white")
        self._tower_name.pack(side=tk.TOP, padx=40, expand=1, fill=tk.X)
        self._tower_name.bind("<Button-1>", self.choose_tower)

        self._tower = tower
        # draw tower price
        self._tower_price = tk.Label(self._bind,
                                     text="{0} coins".format(tower.get_value()),
                                     bg='#4B2E49', fg="white")
        self._tower_price.pack(side=tk.TOP, padx=40)
        self._tower_price.bind("<Button-1>", self.choose_tower)

        # Set Enter and leave for each widget.
        self._tower_name.bind("<Enter>", self.change_active)
        self._tower_name.bind("<Leave>", self.change_inactive)
        self._tower_price.bind("<Enter>", self.change_active)
        self._tower_price.bind("<Leave>", self.change_inactive)
        self._canvas.bind("<Enter>", self.change_active)
        self._canvas.bind("<Leave>", self.change_inactive)
        self._bind.bind("<Enter>", self.change_active)
        self._bind.bind("<Leave>", self.change_inactive)

    def update_price(self):
        """update the price for each tower when the user selects a game level"""
        self._tower_price.destroy()
        self._tower_price = tk.Label(self._bind,
                                     text="{0} coins".format(
                                         self._tower.get_value()),
                                     bg='#4B2E49', fg="white")
        self._tower_price.pack(side=tk.TOP, padx=40)

    def choose_tower(self, event):
        """Choose a tower to show the preview of this tower"""
        self.click_command()

    def change_active(self, event):
        """Change the background colour when the mouse moves to tower area"""
        self._canvas.configure(bg="#4B3B4A")
        self._bind.configure(bg="#4B3B4A")
        self._tower_name.configure(bg="#4B3B4A")
        self._tower_price.configure(bg="#4B3B4A")

    def change_inactive(self, event):
        """Change the background colour when the mouse leaves tower area"""
        self._canvas.configure(bg="#4B2E49")
        self._bind.configure(bg="#4B2E49")
        self._tower_name.configure(bg="#4B2E49")
        self._tower_price.configure(bg="#4B2E49")

    def red_text(self, is_affordable):
        """Change the text colour of a certain tower to red
        if the user cannot afford this tower
        """
        if not is_affordable:
            self._tower_name.configure(fg='red')
            self._tower_price.configure(fg='red')
        else:
            self._tower_name.configure(fg='white')
            self._tower_price.configure(fg='white')


# Task 1.1 (App Class): Instantiate the GUI here
# ...


def main():
    root = tk.Tk()
    app = TowerGameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
