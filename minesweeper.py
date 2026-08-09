from tkinter import *
from tkinter import ttk
from random import randint
import time
import threading

class Tile(Button):
    FLAG = chr(0x2691)
    MINE = chr(0x26ab)
    PICKAXE = chr(0x26cf)

    def __init__(self, x: int, y: int, frm: ttk.Frame, plant_mine: bool = False, safe_spot = False):
        # initialize instance variables
        self.x = x
        self.y = y
        self.is_mine = plant_mine
        self.threat_level = None    # initialize to None; will be calculated after the entire minefield has been generated
        self.adjacent = None        # initialize to None; will be calculated after the entire minefield has been generated
        self.reveal_text = None     # initialize to None; will be calculated after the entire minefield has been generated

        # call parent constructor
        super().__init__(
            frm,
            text=Tile.PICKAXE if safe_spot else '',
            command=self.do_nothing,
            width=2,
            height=1,
            disabledforeground='#ff0000' if self.is_mine else '#000000'
        )

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
        # check if this is the start of the game; if it is, signal that the game has become active
        if not self.master.master.game_active.is_set():
            self.master.master.start_game()

        # reveal this tile
        self.reveal()

        # if this tile is safe, reveal the adjacent tiles
        if self.threat_level == 0:
            for tile in self.adjacent:
                if tile.threat_level == 0 and tile.cget('state') != DISABLED:
                    tile.chain_reveal(event)
                else:
                    tile.reveal()

    def do_nothing(self):
        return

    def reveal(self):
        # if tile is already revealed, don't bother
        if self.cget('state') == DISABLED:
            return

        # check if tile is marked; if it is, don't reveal it and just exit the function
        if self.cget('text') == Tile.FLAG:
            return

        board = self.master.master # get pointer to the board for easier access
        
        # decide what the button text will be; if this is a mine, increase the casualty count by updating the info panel
        if self.is_mine:
            board.update_info_panel(casualty=True) # increment casualties

            # if casualties + flags = num_mines, make the big button green
            if board.game_active.is_set():
                if board.check_totals():
                    board.big_button.config(bg=board.BUTTON_PASSED_COLOR)
                else:
                    board.big_button.config(bg=board.BUTTON_DEFAULT_COLOR)

        # configure button
        self.config(
            text=self.reveal_text,
            state=DISABLED,
            bg=board.BUTTON_REVEALED_COLOR
        )

    def mark_unmark(self, event):
        # if button is disabled, exit the function
        if self.cget('state') == DISABLED:
            return

        board = self.master.master # get pointer to the board for easier access

        # unmark tile if marked
        if self.cget('text') == Tile.FLAG:
            self.config(text='') # set tile text to blank
            board.update_info_panel(flag_increment=False) # decrement flag count of Minefield master Frame

        # mark tile if unmarked
        else:
            self.config(text=Tile.FLAG) # set tile text to flag
            board.update_info_panel(flag_increment=True) # increment flag count of Minefield master Frame

        # if casualties + flags = num_mines, make the big button green
        if board.check_totals():
            board.big_button.config(bg=board.BUTTON_PASSED_COLOR)
        else:
            board.big_button.config(bg=board.BUTTON_DEFAULT_COLOR)

class Minefield(ttk.Frame):
    def __init__(self, board: Tk, width: int, height: int, num_mines: int):
        # initialize instance variables
        self.width = width
        self.height = height
        self.num_mines = num_mines

        super().__init__(board, padding=0) # call parent constructor function

    def load(self):
        # generate the minefield in the Frame
        safe_spot = (int(self.width/2), int(self.height/2))
        self.plant_mines(safe_spot, self.generate_minefield_random(safe_spot))

        # iterate over all tiles
        for tile in self.grid_slaves():
            tile.generate_adjacent()
            tile.calculate_threat_level()

    def reset(self):
        # TODO: implement
        pass

    def generate_minefield_test(self, safe_spot: tuple[int, int]) -> tuple[tuple[int, int]]:
        result = [] # will store coordinate pairs

        # generate simple coordinates
        for y in range(self.height):
            for x in range(self.width):

                # check if done
                if len(result) == self.num_mines:
                    return tuple(result)

                # skip safe spot
                if (x, y) == safe_spot:
                    continue

                # plant mines starting from the upper left corner going to the right until mines run out
                result.append((x, y))

    def generate_minefield_random(self, safe_spot: tuple[int, int]) -> tuple[tuple[int, int]]:
            result = [] # will store coordinate pairs
            mines_planted = 0 # will store the # of mines planted
            
            # generate coordinates
            while mines_planted < self.num_mines:

                # generate random coordinates
                coords = (randint(0, self.width - 1), randint(0, self.height - 1))

                # if this is the safe spot (or adjacent to it), try a different spot
                if (coords[0] in (safe_spot[0] - 1, safe_spot[0], safe_spot[0] + 1)) and (coords[1] in (safe_spot[1] - 1, safe_spot[1], safe_spot[1] + 1)):
                    continue

                # if these coordinates have not already been picked, add them to the results list
                if coords not in result:
                    result.append(coords)
                    mines_planted += 1

            # return the coordinates
            return tuple(result)

    def plant_mines(self, safe_spot: tuple[int, int], mine_coords: tuple[tuple[int, int]]):
        mines_planted = 0 # keep track of how many mines have been planted
        
        # create tile buttons in frame
        for y in range(self.height):
            for x in range(self.width):

                # if these coordinates are one of the pairs listed, plant a mine
                plant_mine = False
                if (x, y) in mine_coords:
                    plant_mine = True
                    mines_planted += 1

                # figure out if this is the safe spot
                is_safe_spot = ((x, y) == safe_spot)

                # create the tile
                Tile(x, y, self, plant_mine, is_safe_spot).grid(column=x, row=y)

    def all_clear_march(self):
        # initialize variables
        speed = 0.02

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
            tile.config(bg=self.master.BUTTON_PASSED_COLOR)
            tile.update_idletasks()

class Info_Panel(ttk.Frame):
    def __init__(self, board: Tk):
        ttk.Style().configure('Info_Panel.TFrame', background='black') # create custom style
        super().__init__(board, style='Info_Panel.TFrame') # call super constructor

        # create labels
        Label(self, text='Casualties', bg='#000000', fg='#ff0000').grid(row=0, column=0, sticky='ew')
        Label(self, text='Time', bg='#000000', fg='#ffff00').grid(row=0, column=1, sticky='ew')
        Label(self, text='Flags', bg='#000000', fg='#8080ff').grid(row=0, column=2, sticky='ew')

        # create StringVars for counter Labels
        self.casualties = StringVar()
        self.duration = StringVar()
        self.flags = StringVar()

        # initialize StringVar text
        self.casualties.set('0')
        self.duration.set('00:00:00')
        self.flags.set('0')

        # create counters
        Label(self, textvariable=self.casualties, bg='#000000', fg='#ff0000').grid(row=1, column=0, sticky='ew')
        Label(self, textvariable=self.duration, bg='#000000', fg='#ffff00').grid(row=1, column=1, sticky='ew')
        Label(self, textvariable=self.flags, bg='#000000', fg='#8080ff').grid(row=1, column=2, sticky='ew')

        # configure columns to expand evenly
        for col in (0, 1, 2):
            self.grid_columnconfigure(col, weight=1)

    def reset(self):
        # reset to default values
        self.casualties.set('0')
        self.duration.set('00:00:00')
        self.flags.set('0')

class Agent_Panel(ttk.Frame):
    AGENT = chr(0x26d1)

    def __init__(self, board: Tk, num_agents: int):
        ttk.Style().configure('Agent_Panel.TFrame', background='black') # create custom style
        super().__init__(board, style='Info_Panel.TFrame') # call super constructor

        # create title Label
        Label(self, text='AGENTS', bg='#000000', fg='#00ff00').pack()

        # create Label for each agent
        self.agent_labels = [] # start with empty list that will store all agent Labels
        for i in range(num_agents):
            self.agent_labels.append(Label(self, text=Agent_Panel.AGENT, bg='#000000', fg='#00ff00'))
            self.agent_labels[-1].pack()

    def remove_agent(self):
        self.agent_labels.pop().destroy()

class Board(Tk):
    def __init__(self, width: int, height: int, num_mines: int):
        # initialize instance variables
        self.casualties = 0 # the # of casualties that have ocurred (each mine tile revealed)
        self.duration = 0 # time in seconds since game has started
        self.flags = 0 # the # of flags currently placed
        self.game_active = threading.Event() # event to signal to the clock thread when to be actively counting

        super().__init__() # call super constructor
        self.title("Minesweeper") # set title bar text
        self.config(bg='#000000') # set background color of window
        self.protocol('WM_DELETE_WINDOW', self.on_close) # bind window close action to function

        # create information panel
        self.info_panel = Info_Panel(self)
        self.info_panel.grid(row=0, column=0, sticky='ew')

        # create minefield
        self.minefield = Minefield(self, width, height, num_mines) # create Minefield Frame in Board
        self.minefield.load() # call load function on Minefield instance after initialization (required)
        self.minefield.grid(row=1, column=0, padx=10)

        # create Agent Panel
        self.agent_panel = Agent_Panel(self, 10)
        self.agent_panel.grid(row=1, column=1, padx=10)

        # create big button
        self.big_button = Button(self, command=self.end_game, text="Signal 'All Clear!'")
        self.big_button.grid(row=2, column=0, padx=200, pady=20)

        # button/tile colors
        self.BUTTON_DEFAULT_COLOR = self.big_button.cget('bg') # store default bg color for later
        self.BUTTON_PASSED_COLOR = '#88ffbb'
        self.BUTTON_REVEALED_COLOR = '#cccccc'

        # create thread that will tick the time up each second
        self.clock = threading.Thread(target=self.run_clock, daemon=True) # create Thread
        self.clock.start() # start clock Thread

    def reset(self):
        self.casualties = 0 # the # of casualties that have ocurred (each mine tile revealed)
        self.duration = 0 # time in seconds since game has started
        self.flags = 0 # the # of flags currently placed
        self.game_active.clear() # event to signal to the clock thread when to be actively counting; should already be cleared at this point, just being safe
        self.info_panel.reset() # reset info panel
        self.minefield.reset() # reset the minefield

        # TODO: reset big button

    def start_game(self):
        self.game_active.set() # event to signal to the clock thread when to be actively counting

    def end_game(self):
        self.game_active.clear() # signal the clock to stop

        # reveal all tiles on the board one at a time
        self.minefield.all_clear_march()

        # TODO: impose some sort of penalty for marking more tiles than needed

        # TODO: transform the big button to reset everything on press

    def run_clock(self):
        while True:
            time.sleep(1)
            if self.game_active.is_set():
                self.duration += 1 # increment
                self.info_panel.duration.set(time.strftime('%H:%M:%S', time.gmtime(self.duration)))

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
        self.game_active.clear()
        self.destroy()

if __name__ == "__main__":
    board = Board(25, 25, 100)
    board.mainloop()