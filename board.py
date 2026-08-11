from tkinter import *
from tkinter import ttk
from random import randint
import time
import threading

class Tile(Label):
    # special characters
    FLAG = chr(0x2691)
    MINE = chr(0x26ab)
    PICKAXE = chr(0x26cf)

    # colors
    FG_COLOR = '#1a1abb'
    REVEALED_COLOR = '#cccccc'
    DEFAULT_COLOR = 'SystemButtonFace'
    MARCH_COLOR = '#88ffbb'

    def __init__(self, x: int, y: int, frm: ttk.Frame):
        # initialize instance variables
        self.x = x
        self.y = y
        self.is_mine = False        # initialize to False; will be set if necessary during minefield generation
        self.threat_level = None    # initialize to None; will be calculated after the entire minefield has been generated
        self.adjacent = None        # initialize to None; will be calculated after the entire minefield has been generated
        self.reveal_text = None     # initialize to None; will be calculated after the entire minefield has been generated

        # call parent constructor
        super().__init__(
            frm,
            text='',
            width=2,
            height=1,
            disabledforeground='#000000',
            fg=Tile.FG_COLOR
        )

        # bind mouse click events
        self.bind('<Button-1>', self.chain_reveal)
        self.bind('<Button-3>', self.mark_unmark)

    def generate_adjacent(self):
        result = [] # start with empty list; will store all (x, y) coordinates as tuples within list
        width, height = self.master.grid_size() # store width and height of minefield

        # iterate thru 3x3 square with (x, y) at the center
        for j in (self.y - 1, self.y, self.y + 1):
            for i in (self.x - 1, self.x, self.x + 1):

                # if this is the middle tile (the one we're generating this for), skip
                if j == self.y and i == self.x:
                    continue

                # if x coordinate is outside the valid range, skip
                if i < 0 or i >= width:
                    continue

                # if y coordinate is outside the valid range, skip
                if j < 0 or j >= height:
                    continue

                # add Button to result
                result.append(self.master.grid_slaves(column=i, row=j)[0])

        self.adjacent = tuple(result)

    def calculate_threat_level(self):
        # if this tile is a mine, set threat level to 9 and be done
        if self.is_mine:
            self.threat_level = 9
            self.reveal_text = Tile.MINE
            return

        self.threat_level = 0 # start with 0, will add one for each adjacent mine

        # iterate thru adjacent tiles and increment for each mine
        for tile in self.adjacent:
            if tile.is_mine:
                self.threat_level += 1 # mine detected

        # set reveal text
        if self.threat_level == 0:
            self.reveal_text = ''
        else:
            self.reveal_text = str(self.threat_level)

    def chain_reveal(self, event):
        board = self.master.master # grab pointer to Board for easier access

        # depending on game state, exit function immediately (do not allow left-click to reveal tiles)
        if board.game_state in (GameState.END, GameState.PAUSED):
            return

        # check if the game is in the ready state; if it is, start the game
        if board.game_state == GameState.READY:
            board.start_game()

        # reveal this tile
        self.reveal()

        # if this tile is safe, do some recursive magic
        if self.threat_level == 0:
            for tile in self.adjacent:
                if tile.threat_level == 0 and tile.cget('state') != DISABLED:
                    tile.chain_reveal(event)
                else:
                    tile.reveal()

    def reveal(self):
        # if tile is already revealed, don't bother
        if self.cget('state') == DISABLED:
            return

        # check if tile is marked; if it is, don't reveal it and just exit the function
        if self.cget('text') == Tile.FLAG:
            return

        board = self.master.master # get pointer to the board for easier access
        
        # increase the casualty count by updating the info panel
        if self.is_mine:
            board.update_info_panel(casualty=True) # increment casualties

            # if casualties + flags = num_mines, make the 'all clear' button green
            if board.game_state == GameState.ACTIVE:
                if board.check_totals():
                    board.all_clear_button.config(bg=Tile.MARCH_COLOR)
                else:
                    board.all_clear_button.config(bg=Tile.DEFAULT_COLOR)
                board.all_clear_button.update_idletasks()

        # configure button
        self.config(
            text=self.reveal_text,
            state=DISABLED,
            bg=Tile.REVEALED_COLOR
        )

    def mark_unmark(self, event):
        # if button is disabled, exit the function
        if self.cget('state') == DISABLED:
            return

        board = self.master.master # get pointer to the board for easier access

        # depending on game state, exit the function (do not mark)
        if board.game_state in (GameState.PAUSED, GameState.END, GameState.READY):
            return

        # unmark tile if marked
        if self.cget('text') == Tile.FLAG:
            self.config(text='') # set tile text to blank
            board.update_info_panel(flag_increment=False) # decrement flag count of Minefield master Frame

        # mark tile if unmarked
        else:
            self.config(text=Tile.FLAG) # set tile text to flag
            board.update_info_panel(flag_increment=True) # increment flag count of Minefield master Frame

        # if casualties + flags = num_mines, make the 'all clear' button green
        if board.check_totals():
            board.all_clear_button.config(bg=Tile.MARCH_COLOR)
        else:
            board.all_clear_button.config(bg=Tile.DEFAULT_COLOR)
        board.all_clear_button.update_idletasks()

    def reset(self):
        # reset tile button configuration
        self.config(
            state=NORMAL,
            text='',
            disabledforeground='#000000',
            fg=Tile.FG_COLOR,
            bg=Tile.DEFAULT_COLOR
        )

        # reset variables
        self.is_mine = False        # initialize to False; will be set if necessary during minefield generation
        self.threat_level = None    # initialize to None; will be calculated after the entire minefield has been generated
        self.adjacent = None        # initialize to None; will be calculated after the entire minefield has been generated
        self.reveal_text = None     # initialize to None; will be calculated after the entire minefield has been generated

class Minefield(ttk.Frame):
    def __init__(self, board: Tk, width: int, height: int, num_mines: int):
        # initialize instance variables
        self.width = width
        self.height = height
        self.num_mines = num_mines

        ttk.Style().configure('Minefield.TFrame', background='black') # create custom style
        super().__init__(board, padding=0, style='Minefield.TFrame') # call parent constructor function
        self.create_tiles()

    def load(self):
        # generate the minefield in the Frame
        safe_spot = (int(self.width/2), int(self.height/2)) # decide the safe spot; for now, putting it in the middle of the minefield is good enough
        self.plant_mines(Minefield.generate_random_coords(self.width, self.height, self.num_mines, safe_spot)) # plant the mines randomly
        self.grid_slaves(column=safe_spot[0], row=safe_spot[1])[0].config(text=Tile.PICKAXE) # mark the safe spot

        # iterate over all tiles
        for tile in self.grid_slaves():
            tile.generate_adjacent()
            tile.calculate_threat_level()

    def reset(self):
        # iterate thru all tiles
        for tile in self.grid_slaves():
            tile.reset()

        self.load() # reload

    def create_tiles(self):
        # create tile Buttons in Frame
        for y in range(self.height):
            for x in range(self.width):
                Tile(x, y, self).grid(column=x, row=y, padx=1, pady=1)

    def generate_random_coords(width: int, height: int, num_mines: int, safe_spot: tuple[int, int]) -> tuple[tuple[int, int]]:
            result = [] # will store coordinate pairs
            mines_planted = 0 # will store the # of mines planted
            
            # generate coordinates
            while mines_planted < num_mines:

                # generate random coordinates
                coords = (randint(0, width - 1), randint(0, height - 1))

                # if this is the safe spot (or adjacent to it), try a different spot
                if (coords[0] in (safe_spot[0] - 1, safe_spot[0], safe_spot[0] + 1)) and (coords[1] in (safe_spot[1] - 1, safe_spot[1], safe_spot[1] + 1)):
                    continue

                # if these coordinates have not already been picked, add them to the results list
                if coords not in result:
                    result.append(coords)
                    mines_planted += 1

            # return the coordinates
            return tuple(result)

    def plant_mines(self, mine_coords: tuple[tuple[int, int]]):
        # iterate thru mine_coords, plant mines
        for coord in mine_coords:
            tile = self.grid_slaves(column=coord[0], row=coord[1])[0] # grab tile for easy access
            tile.is_mine = True
            tile.config(disabledforeground='#ff0000')

    def all_clear_march(self):
        # initialize variables
        speed = 0.0003

        # iterate through all tiles in the minefield
        for tile in self.grid_slaves():
            # reveal the tile after an amount of time
            time.sleep(speed)
            tile.reveal()

            # TODO: Should this count against the player? Maybe as a casualty...
            # if tile is marked but is not a mine, make the flag red
            if tile.cget('text') == Tile.FLAG and not tile.is_mine:
                tile.config(fg='#ff0000')

            # change the tile color to show that it has been passed
            tile.config(bg=Tile.MARCH_COLOR)
            tile.update_idletasks()

        # iterate back thru all tiles and change color back
        for tile in self.grid_slaves():
            # wait for same time as before
            time.sleep(speed)

            # if tile is disabled, go with the revealed bg color
            if tile.cget('state') == DISABLED:
                tile.config(bg=Tile.REVEALED_COLOR)

            # if tile hasn't been revealed (is marked), go with the default color
            else:
                tile.config(bg=Tile.DEFAULT_COLOR)

            tile.update_idletasks() # update idle tasks so changes appear immediately

class Info_Panel(ttk.Frame):
    PAUSE_SYMBOL = chr(0x23f8)
    PLAY_SYMBOL = chr(0x23f5)

    def __init__(self, board: Tk):
        ttk.Style().configure('Info_Panel.TFrame', background='black') # create custom style
        super().__init__(board, style='Info_Panel.TFrame') # call super constructor

        # create Labels
        Label(self, text='Casualties', bg='#000000', fg='#ff0000').grid(row=0, column=0, sticky='e')
        Label(self, text='Time', bg='#000000', fg='#ffff00').grid(row=0, column=1, columnspan=2)
        Label(self, text='Flags', bg='#000000', fg='#8080ff').grid(row=0, column=3, sticky='w')

        # create StringVars for counter Labels
        self.casualties = StringVar()
        self.duration = StringVar()
        self.flags = StringVar()

        # initialize StringVar text
        self.casualties.set('0')
        self.duration.set('00:00:00')
        self.flags.set('0')

        # configure columns
        for col in (0, 1, 2, 3):
            self.columnconfigure(col, weight=1, uniform='info_cols')

        # create counters & pause button
        Label(self, textvariable=self.casualties, bg='#000000', fg='#ff0000').grid(row=1, column=0, sticky='e')
        Label(self, textvariable=self.duration, bg='#000000', fg='#ffff00').grid(row=1, column=1, sticky='e', padx=5)
        self.pause_button = Button(self, text=Info_Panel.PAUSE_SYMBOL, command=self.master.pause_unpause, padx=5, pady=5)
        self.pause_button.grid(row=1, column=2, sticky='w', padx=5)
        Label(self, textvariable=self.flags, bg='#000000', fg='#8080ff').grid(row=1, column=3, sticky='w')

        # configure columns to expand evenly
        for col in (0, 1, 2):
            self.grid_columnconfigure(col, weight=1)

    def reset(self):
        # reset to default values
        self.casualties.set('0')
        self.duration.set('00:00:00')
        self.flags.set('0')
        self.pause_button.config(text=Info_Panel.PAUSE_SYMBOL)

class GameState:
    READY = 'ready'
    ACTIVE = 'active'
    PAUSED = 'paused'
    END = 'end'

class Data:
    def __init__(self, *data):
        self.data = data

    def update(self, *data):
        self.data = data

    def get(self):
        return self.data

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

class Board(Tk):
    def __init__(self, width: int, height: int, mine_count: int):
        # initialize instance variables
        self.casualties = 0 # the # of casualties that have ocurred (each mine tile revealed)
        self.duration = 0 # time in seconds since game has started
        self.flags = 0 # the # of flags currently placed
        self.game_state = GameState.READY # initialize the game state to 'ready'
        self.clock_active = threading.Event() # event to signal to the clock thread when to be actively counting

        super().__init__() # call super constructor
        self.title("Minesweeper") # set title bar text
        self.config(bg='#000000') # set background color of window
        self.protocol('WM_DELETE_WINDOW', self.on_close) # bind window close action to function

        # create information panel
        self.info_panel = Info_Panel(self)
        self.info_panel.grid(row=0, column=0, sticky='ew', columnspan=2)

        # create minefield
        self.minefield = Minefield(self, width, height, mine_count) # create Minefield Frame in Board
        self.minefield.load() # call load function on Minefield instance after initialization (required)
        self.minefield.grid(row=1, column=0, padx=10, columnspan=2)

        # create 'all clear' button
        self.all_clear_button = Button(self, command=self.end_game, text='Signal "All Clear!"', state=DISABLED)
        self.all_clear_button.grid(row=2, column=0, padx=30, pady=20, sticky='e')

        # create 'reset' button
        self.reset_button = Button(self, command=self.reset, text="Reset Board")
        self.reset_button.grid(row=2, column=1, padx=30, pady=20, sticky='w')

        # create thread that will tick the time up each second
        self.clock = threading.Thread(target=self.run_clock, daemon=True) # create Thread
        self.clock.start() # start clock Thread

    def reset(self):
        self.casualties = 0 # the # of casualties that have ocurred (each mine tile revealed)
        self.duration = 0 # time in seconds since game has started
        self.flags = 0 # the # of flags currently placed
        self.game_state = GameState.READY # set game state to 'ready'
        self.clock_active.clear() # event to signal to the clock thread when to be actively counting
        self.info_panel.reset() # reset info panel
        self.minefield.reset() # reset the minefield
        self.all_clear_button.config(bg=Tile.DEFAULT_COLOR, state=DISABLED) # reset the button to its default color & disable it

    def start_game(self):
        self.game_state = GameState.ACTIVE # set the game state to 'active'
        self.clock_active.set() # signal to the clock to start counting
        self.all_clear_button.config(state=ACTIVE)

    def end_game(self):
        self.game_state = GameState.END # set game state to 'end'
        self.clock_active.clear() # signal the clock to stop
        self.all_clear_button.config(bg=Tile.DEFAULT_COLOR, state=DISABLED) # reset the button to its default color & disable it
        self.minefield.all_clear_march() # reveal all tiles on the board one at a time

    def run_clock(self):
        while True:
            time.sleep(1)
            if self.clock_active.is_set():
                self.duration += 1 # increment
                self.info_panel.duration.set(time.strftime('%H:%M:%S', time.gmtime(self.duration)))
            else:
                self.info_panel.duration.set('PAUSED')

    def pause_unpause(self):
        # if game is paused, unpause it
        if self.game_state == GameState.PAUSED:
            self.game_state = GameState.ACTIVE  # set game state back to 'active'
            self.clock_active.set()             # set the clock flag
            self.info_panel.pause_button.config(text=Info_Panel.PAUSE_SYMBOL) # change the button text to display the pause symbol

        # if game is active, pause it
        elif self.game_state == GameState.ACTIVE:
            self.clock_active.clear()           # clear the clock flag
            self.game_state = GameState.PAUSED  # set the game state to 'paused'
            self.info_panel.pause_button.config(text=Info_Panel.PLAY_SYMBOL) # change the button text to display the play symbol

    def update_info_panel(self, casualty: bool = False, flag_increment: bool = None):
        # updating casualty counter
        if casualty:
            self.casualties += 1 # increment
            self.info_panel.casualties.set(str(self.casualties))

        # updating the flag counter
        if flag_increment is not None:

            # incrementing
            if flag_increment:
                self.flags += 1
                self.info_panel.flags.set(str(self.flags))

            # decrementing
            else:
                self.flags -= 1
                self.info_panel.flags.set(str(self.flags))

    def check_totals(self) -> bool:
        return ((self.casualties + self.flags) == self.minefield.num_mines)

    def on_close(self):
        self.clock_active.clear()
        self.destroy()

if __name__ == "__main__":
    board = Board(25, 25, 10)
    board.mainloop()