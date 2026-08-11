from board import Board, Data
from configure_window import ConfigureWindow
import sys

if __name__ == '__main__':
    # get dimensions from ConfigureWindow
    data = Data()
    cw = ConfigureWindow(data)
    cw.mainloop()

    # if data is empty, exit the program
    if len(data) == 0:
        sys.exit(0)

    # create the board
    board = Board(*data.get())
    board.mainloop()