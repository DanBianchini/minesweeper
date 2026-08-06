from tkinter import *
from tkinter import ttk
from random import randint

class Tile(Button):
    FLAG = chr(0x2691)
    MINE = chr(0x26ab)
    PICKAXE = chr(0x26cf)

    def __init__(self, x: int, y: int, frm: ttk.Frame, plant_mine: bool = False, safe_spot = False):
        # initialize instance variables
        self.x = x
        self.y = y
        self.is_mine = plant_mine
        self.threat_level = None # initialize to None; will be calculated after the entire minefield has been generated
        self.adjacent = None # initialize to None; will be calculated after the entire minefield has been generated

        # call parent constructor
        super().__init__(
            frm,
            text=Tile.PICKAXE if safe_spot else '',
            command=self.chain_reveal,
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
        # if this tile is a mine, set threat level to 9 and be done
        if self.is_mine:
            self.threat_level = 9
            return

        self.threat_level = 0 # start with 0, will add one for each adjacent mine

        # iterate thru adjacent tiles and increment for each mine
        for tile in self.adjacent:
            if tile.is_mine:
                self.threat_level += 1 # mine detected

    def chain_reveal(self):
        # reveal this tile
        self.reveal()

        # if this tile is safe, reveal the adjacent tiles
        if self.threat_level == 0:
            for tile in self.adjacent:
                if tile.threat_level == 0 and tile.cget('state') != DISABLED:
                    tile.chain_reveal()
                else:
                    tile.reveal()

    def reveal(self):
        # if tile is already revealed, don't bother
        if self.cget('state') == DISABLED:
            return

        # check if tile is marked; if it is, don't reveal it and just exit the function
        if self.cget('text') == Tile.FLAG:
            return
        
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
        self.flag_count = 0

        # create board
        self.board = Tk() # create board
        self.board.title("Minesweeper") # set title bar text

        # create minefield Frame
        self.minefield = ttk.Frame(self.board, padding=0) # create frame in board
        self.minefield.grid()

        # generate the minefield in the 'minefield' Frame
        safe_spot = (int(width/2), int(height/2))
        Minesweeper.plant_mines(self.minefield, width, height, safe_spot, *Minesweeper.generate_minefield_random(self.minefield, width, height, num_mines, safe_spot))

    def load(self):
        # iterate over all tiles
        for tile in self.minefield.grid_slaves():
            tile.generate_adjacent()
            tile.calculate_threat_level()

    def generate_minefield_test(minefield: ttk.Frame, width: int, height: int, num_mines: int, safe_spot: tuple[int, int]) -> tuple[tuple[int, int]]:
        result = [] # will store coordinate pairs

        # generate simple coordinates
        for y in range(height):
            for x in range(width):

                # check if done
                if len(result) == num_mines:
                    return tuple(result)

                # skip safe spot
                if (x, y) == safe_spot:
                    continue

                # plant mines starting from the upper left corner going to the right until mines run out
                result.append((x, y))

    def generate_minefield_random(minefield: ttk.Frame, width: int, height: int, num_mines: int, safe_spot: tuple[int, int]) -> tuple[tuple[int, int]]:
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

    def plant_mines(minefield: ttk.Frame, width: int, height: int, safe_spot: tuple[int, int], *mine_coords: tuple[int, int]):
        mines_planted = 0 # keep track of how many mines have been planted
        
        # create tile buttons in frame
        for y in range(height):
            for x in range(width):
                # if these coordinates are one of the pairs listed, plant a mine
                plant_mine = False
                if (x, y) in mine_coords:
                    plant_mine = True
                    mines_planted += 1

                # figure out if this is the safe spot
                is_safe_spot = ((x, y) == safe_spot)

                # create the tile
                Tile(x, y, minefield, plant_mine, is_safe_spot).grid(column=x, row=y)

if __name__ == "__main__":
    ms = Minesweeper(25, 25, 150)
    ms.load()
    ms.board.mainloop()