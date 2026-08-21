from tkinter import *
from board import Minefield, Tile
import time
from random import randint

# ===== RESET COLOR FUNCTIONS =====

def reset_color(tile: Tile):
    if tile.cget('state') == DISABLED:
        tile.config(bg=Tile.REVEALED_COLOR)
    else:
        tile.config(bg=Tile.DEFAULT_COLOR)

def reset_colors(minefield: Minefield):
    for tile in minefield.grid_slaves():
        reset_color(tile)

# ===== ANIMATIONS =====

def simple_rainbow(minefield: Minefield):
    rainbow = ('#ff0000', '#ff7f00', '#ffff00', '#7fff00', '#00ff00', '#00ff7f', '#00ffff', '#007fff', '#0000ff', '#7f00ff', '#ff00ff', '#ff007f')

    for i in range(3):
        for color in rainbow:
            for tile in minefield.grid_slaves():
                tile.config(bg=color)
            minefield.update_idletasks()
            time.sleep(0.05)

    reset_colors(minefield)
    minefield.update_idletasks()

def simple_color(minefield: Minefield, color: str = '#000000'):
    # turn entire minefield specified color
    for tile in minefield.grid_slaves():
        tile.config(bg=color)
        tile.update_idletasks()
        time.sleep(0.001)

    # reset all tile colors
    for tile in minefield.grid_slaves():
        reset_color(tile)
        tile.update_idletasks()
        time.sleep(0.001)

def random_fill(minefield: Minefield):
    # turn entire minefield specified black
    for tile in minefield.grid_slaves():
        tile.config(bg='#000000')
        tile.update_idletasks()
        time.sleep(0.001)

    # get list of all tiles
    all_tiles = minefield.grid_slaves()

    # pick random tiles until all tile colors have been reset
    while len(all_tiles) > 0:
        time.sleep(0.001)
        tile = all_tiles.pop(randint(0, len(all_tiles) - 1))
        reset_color(tile)
        tile.update_idletasks()

# ===== TEST CODE =====

def test_rainbow():
    simple_rainbow(mf)

def test_simple_color():
    simple_color(mf, '#00ff00')

def test_random_fill():
    random_fill(mf)

if __name__ == '__main__':
    window = Tk()
    mf = Minefield(window, 25, 25, 10)
    mf.pack()
    frm = Frame(window, bg='#000000')
    frm.pack()
    Button(frm, text='Simple Rainbow', command=test_rainbow).grid(column=0, row=0)
    Button(frm, text='Simple Color', command=test_simple_color).grid(column=1, row=0)
    Button(frm, text='Random Fill', command=test_random_fill).grid(column=2, row=0)
    window.mainloop()