from tkinter import *
from minesweeper import Tile

def get_title_art():
    with open('title_art', encoding='utf-8') as f:
        return f.read()

class DataEntry(Frame):
    def __init__(self, window: Tk, name: str):
        # call parent constructor
        super().__init__(
            window,
            borderwidth=1,
            relief='solid'
        )

        # create field name label
        Label(self, text= name + ':', padx=5, pady=5).grid(column=0, row=0, sticky='e')

        # create data entry box
        self.data_entry = Entry(self, width=5)
        self.data_entry.grid(column=1, row=0, sticky='ew')

        # create error message display label
        self.error_message = StringVar()
        self.error_message.set('')
        Label(self, textvariable=self.error_message, fg='#ff0000', width=30).grid(column=2, row=0, sticky='w')

    def get_info(self):
        try:
            return int(self.data_entry.get())
        except ValueError:
            self.error_message.set("Unable to convert to an integer")
            return None

class ConfigureWindow(Tk):
    # color class variables
    PRIMARY_COLOR = Tile.DEFAULT_COLOR
    SECONDARY_COLOR = Tile.FG_COLOR

    def __init__(self):
        super().__init__()
        self.title('Minefield Setup')
        self.config(bg=ConfigureWindow.PRIMARY_COLOR)

        # create Title Art Label
        Label(
            self,
            text=get_title_art(),
            padx=10,
            pady=10,
            borderwidth=1,
            relief='solid',
            font=('Consolas', 10, 'normal'),
            fg=ConfigureWindow.SECONDARY_COLOR,
            bg=ConfigureWindow.PRIMARY_COLOR
        ).grid(column=0, row=0, padx=20, pady=20)

        # create data entry boxes
        self.data_entries = [] # initialize with empty list
        for name in ('Width', 'Height', 'Mine Count'):
            self.data_entries.append(DataEntry(self, name))
            self.data_entries[-1].grid(column=0, row=len(self.data_entries), padx=5, pady=5)

        # create button at bottom
        Button(
            self,
            text='Confirm',
            command=self.finalize,
            borderwidth=1,
            relief='solid'
        ).grid(column=0, row=4, pady=10)

    def finalize(self):
        for data_entry in self.data_entries:
            data_entry.get_info()

if __name__ == '__main__':
    cw = ConfigureWindow()
    cw.mainloop()