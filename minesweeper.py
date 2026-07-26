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

        # generate adjacent tuple
        self.adjacent = Tile.generate_adjacent(x, y, *frm.grid_size())

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

    def generate_adjacent(x: int, y: int, width: int, height: int) -> tuple[tuple[int,int]]:
        result = [] # start with empty list; will store all (x, y) coordinates as tuples within list

        # iterate thru 3x3 square with (x, y) at the center
        for j in (y - 1, y, y + 1):
            for i in (x - 1, x, x + 1):
                # if this is the middle tile (the one we're generating this for), skip
                if j == y and i == x:
                    continue

                # if x coordinate is outside the valid range, skip
                if i < 0 or i >= width:
                    continue

                # if y coordinate is outside the valid range, skip
                if j < 0 or j >= height:
                    continue

                # add coordinates to result
                result.append((i, j))

        return tuple(result)

    def get_threat_level(self) -> int:
        threat_level = 0 # start with 0, will add one for each adjacent mine

        # iterate thru adjacent tiles and increment for each mine
        for coord in self.adjacent:
            if self.master.grid_slaves(coord[1], coord[0])[0].is_mine:
                threat_level += 1 # mine detected

        return threat_level

    def reveal(self):
        # decide what the button text will be
        if self.is_mine:
            button_text = Tile.MINE
        else:
            threat_level = self.get_threat_level()
            button_text = '' if threat_level == 0 else str(threat_level)

        # configure button
        self.config(
            text=button_text,
            state=DISABLED,
            bg='#B0B0B0'
        )

        # TODO reveal other non-disabled buttons around this one that have a threat_level = 0

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
        minefield = ttk.Frame(self.board, padding=0) # create frame in board
        minefield.grid()

        # generate the minefield in the 'minefield' Frame
        Minesweeper.generate_minefield_test(minefield, width, height, num_mines)

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
    ms.board.mainloop()