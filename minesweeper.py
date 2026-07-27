from tkinter import *
from tkinter import ttk

class Tile(Button):
    FLAG = chr(0x2691)
    MINE = chr(0x26ab)

    def __init__(self, x: int, y: int, frm: ttk.Frame, plant_mine: bool = False):
        # initialize instance variables
        self.x = x
        self.y = y
        self.is_mine = plant_mine
        self.threat_level = None # initialize to None; will be calculated after the entire minefield has been generated
        self.adjacent = None # initialize to None; will be calculated after the entire minefield has been generated

        # call parent constructor
        super().__init__(
            frm,
            text='',
            command=self.reveal,
            width=2,
            height=1,
            disabledforeground='#ff0000' if self.is_mine else '#000000'
        )

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
        self.threat_level = 0 # start with 0, will add one for each adjacent mine

        # iterate thru adjacent tiles and increment for each mine
        for tile in self.adjacent:
            if tile.is_mine:
                self.threat_level += 1 # mine detected

    def reveal(self):
        # decide what the button text will be
        if self.is_mine:
            button_text = Tile.MINE
        else:
            button_text = '' if self.threat_level == 0 else str(self.threat_level)

        # configure button
        self.config(
            text=button_text,
            state=DISABLED,
            bg='#B0B0B0'
        )

        # TODO reveal other non-disabled buttons around this one that have a threat_level = 0
        #for coord in self.adjacent:
            #adj_tile = self.master.grid_slaves(coord[1], coord[0])[0]

    def mark_unmark(self, event):
        # if button is disabled, exit the function
        if self.cget('state') == DISABLED:
            return

        # configure button
        self.config(text=Tile.FLAG if self.cget('text') == '' else '')

class Minesweeper:
    def __init__(self, width: int, height: int, num_mines: int):
        # initialize instance variables
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.num_flags = 0

        # create board + components
        self.board = Tk() # create board
        # TODO potentially save minefield to an instance variable for later if needed
        self.minefield = ttk.Frame(self.board, padding=0) # create frame in board
        self.minefield.grid()

        # generate the minefield in the 'minefield' Frame
        Minesweeper.generate_minefield_test(self.minefield, width, height, num_mines)

    def load(self):
        # iterate over all tiles
        for tile in self.minefield.grid_slaves():
            tile.generate_adjacent()
            tile.calculate_threat_level()

    def generate_minefield_test(minefield: ttk.Frame, width: int, height: int, num_mines: int):
        mines_planted = 0 # keep track of how many mines have been planted

        # create tile buttons in frame
        for y in range(height):
            for x in range(width):

                # determine whether or not this tile will be a mine
                plant_mine = False
                if mines_planted < num_mines: # TODO simple logic for testing for now
                    plant_mine = True
                    mines_planted += 1

                # creat the tile
                Tile(x, y, minefield, plant_mine).grid(column=x, row=y)

if __name__ == "__main__":
    ms = Minesweeper(25, 25, 10)
    ms.load()
    ms.board.mainloop()