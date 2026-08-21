from tkinter import *
from board import Tile

def get_title_art():
    with open('title_art', encoding='utf-8') as f:
        return f.read()

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

class DataField:
    def __init__(self, frm: Frame, row: int, name: str):
        # create field name label
        Label(
            frm,
            text= name + ':',
            padx=5,
            pady=5
        ).grid(column=0, row=row, sticky='e')

        # create data entry box
        self.data_entry = Entry(frm, width=5)
        self.data_entry.grid(column=1, row=row, sticky='ew')

        # create error message display label
        self.error_message = StringVar()
        self.error_message.set('')
        Label(
            frm,
            textvariable=self.error_message,
            fg='#ff0000',
            width=30
        ).grid(column=2, row=row, sticky='w')

    def get_info(self) -> int:
        try:
            self.error_message.set('')
            return int(self.data_entry.get())
        except ValueError:
            self.error_message.set("Unable to convert to an integer")
            return None

class DataEntry(Frame):
    def __init__(self, window: Tk, *field_names: str):
        # call parent constructor
        super().__init__(
            window,
            borderwidth=1,
            relief='solid'
        )

        # create DataFields
        self.data_fields = []
        for name in field_names:
            self.data_fields.append(DataField(self, len(self.data_fields) + 1, name))

    def get_info(self) -> tuple:
        result = [] # initialize result with empty list
        
        # iterate thru data entries, get info
        for data_entry in self.data_fields:
            result.append(data_entry.get_info())

        # if any of the results were None, exit the function
        if None in result:
            return None

        # if we made it to this point, convert results to tuple and return
        return tuple(result)

class ConfigureWindow(Tk):
    # color class variables
    PRIMARY_COLOR = Tile.DEFAULT_COLOR
    SECONDARY_COLOR = Tile.FG_COLOR

    def __init__(self, data: list):
        # set up window
        super().__init__()
        self.title('Minefield Setup')
        self.config(bg=ConfigureWindow.PRIMARY_COLOR)
        self.protocol('WM_DELETE_WINDOW', self.on_close)

        self.data = data # keep a pointer to the Data object supplied

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
        self.data_entry = DataEntry(self, 'Width', 'Height', 'Mine Count')
        self.data_entry.grid(column=0, row=1, padx=10, pady=10)

        # create button at bottom
        Button(
            self,
            text='Confirm',
            command=self.finalize,
            borderwidth=1,
            relief='solid'
        ).grid(column=0, row=4, pady=10)

    def finalize(self):
        data = self.data_entry.get_info() # get data tuple from data entry Frame

        # if data is None, don't go through with the finalization
        if data is None:
            return
        
        self.data.update(*data) # inject the result into the data object and close this window
        self.destroy() # close this window

    def on_close(self):
        self.data.update()
        self.destroy()

if __name__ == '__main__':
    data = Data()
    cw = ConfigureWindow(data)
    cw.mainloop()
    print(data.get())