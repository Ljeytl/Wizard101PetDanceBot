from dataclasses import astuple, dataclass, field
import sys
import threading
from typing import List

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font, messagebox

import dance_game as DG
from properties import Globals, separate


def show_error(title: str, message: str) -> None:
    """Shows error message box without the root window."""
    root = tk.Tk()
    root.overrideredirect(1)
    root.withdraw()
    messagebox.showerror(title=title, message=message)
    root.destroy()


class MessageBox():
    """Shows message box without the root window."""

    def __init__(self, title: str, message: str) -> None:
        self.title = title
        self.message = message

        self.root = tk.Tk()
        self.root.overrideredirect(1)
        self.root.withdraw()

    def destruct(self) -> None:
        self.root.destroy()

    @self_destruct
    def show_error(self) -> None:
        logging.error(self.title, stacklevel=4)
        messagebox.showerror(title=self.title, message=self.message)

    @self_destruct
    def show_warning(self) -> None:
        logging.warning(self.title, stacklevel=4)
        messagebox.showwarning(title=self.tilte, message=self.message)

    @self_destruct
    def show_info(self) -> None:
        logging.info(self.title, stacklevel=4)
        messagebox.showinfo(title=self.title, message=self.message)


def create_frame(master: tk.Frame, **kwargs) -> tk.Frame:
    return tk.Frame(master, bg=kwargs.get('bg', '#f0f0f0'), relief='raised')


class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master: tk.Frame=None, placeholder: str='PLACEHOLDER', color: str='grey', text=None) -> None:
        super().__init__(master)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self['justify'] = 'left'

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        # not a placeholder, use text value if specified
        if text is not None:
            self.insert(tk.END, text)
        else:
            self.put_placeholder()

    def put_placeholder(self) -> None:
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def focus_in(self, *args) -> None:
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def focus_out(self, *args) -> None:
        if not self.get():
            self.put_placeholder()


@dataclass
class ConfigureSettings:
    locations: List[int] = field(default_factory=list)
    snacks: List[int] = field(default_factory=list)
    num_games: int = 1
    resolution: str = ''

    def __iter__(self):
        """Returns the data as a tuple."""
        return iter(astuple(self))


class Configure(tk.Tk):
    configure_settings: ConfigureSettings = None
    def __init__(self) -> None:
        super().__init__()
        self.title("W101 Pet Dance")
        self.geometry("268x248")
        self.eval('tk::PlaceWindow . center') # open window in center of screen
        self.resizable(False, False)
        self.columnconfigure(0, weight=1) # column weight 100%
        self.rowconfigure(0, weight=5) 
        self.rowconfigure(1, weight=2) # change weight to 4
        self.rowconfigure(2, weight=1)
        self.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))

        # adding frames to window
        frame_top = create_frame(self)
        frame_middle = create_frame(self)
        frame_bottom = create_frame(self)
        frame_topleft = create_frame(frame_top)
        frame_topright = create_frame(frame_top)
        frame_middleleft = create_frame(frame_middle)
        frame_middleright = create_frame(frame_middle)

        # placing in grid
        frame_top.columnconfigure(0, weight=1)
        frame_top.columnconfigure(1, weight=1)
        frame_top.rowconfigure(0, weight=1)
        frame_top.grid(row=0, column=0, sticky='nesw')
        frame_topleft.grid(row=0, column=0, sticky='nesw')
        frame_topright.grid(row=0, column=1, sticky='nesw')
        frame_middle.columnconfigure(0, weight=1)
        frame_middle.columnconfigure(1, weight=1)
        frame_middle.rowconfigure(0, weight=1)
        frame_middle.grid(row=1, column=0, sticky='nesw')
        frame_middleleft.grid(row=0, column=0, sticky='nesw')
        frame_middleright.grid(row=0, column=1, sticky='nesw')
        frame_bottom.grid(row=2, column=0, sticky='nesw')

        # add location check boxes
        self.frame_locations(frame_topleft)

        # add snack check boxes
        self.frame_snacks(frame_topright)

        # add "configurations"
        self.configure_games(frame_middleleft)
        self.configure_resolutions(frame_middleright)

        tk.Button(frame_bottom, text='Start', command=self.start, relief='solid', bg='#e1e1e1').pack(expand=True, fill='both', padx=10, pady=10)

    def frame_locations(self, frame: tk.Frame) -> None:
        self.location_boxes = []
        tk.Label(frame, text='Locations to Farm', font=font.Font(size=9, underline=True)).pack(padx=10, pady=(10, 0), anchor='w')
        cities = ['Wizard City', 'Krokotopia', 'Marleybone', 'Mooshu', 'Dragonspyre']

        # use default settings or previously entered settings
        if Configure.configure_settings is None:
            for idx, city in enumerate(cities):
                self.location_boxes.append(tk.IntVar(value=1) if idx == 0 else tk.IntVar())
                self.create_checkbox(frame, anchor='w', text=city, var=self.location_boxes[idx])
        else:
            for idx, (city, location_checked) in enumerate(zip(cities, Configure.configure_settings.locations)):
                self.location_boxes.append(tk.IntVar(value=location_checked))
                self.create_checkbox(frame, anchor='w', text=city, var=self.location_boxes[idx])

    def frame_snacks(self, frame: tk.Frame) -> None:
        self.snack_boxes = []
        tk.Label(frame, text='Pet Snacks to Feed', font=font.Font(size=9, underline=True)).pack(padx=10, pady=(10, 0), anchor='e')
        snacks = [f'Snack {i}' for i in range(1, 6)]

        # use default settings or previously entered settings
        if Configure.configure_settings is None:
            for idx, snack in enumerate(snacks):
                self.snack_boxes.append(tk.IntVar())
                self.create_checkbox(frame, anchor='center', text=snack, var=self.snack_boxes[idx])
        else:
            for idx, (snack, snack_checked) in enumerate(zip(snacks, Configure.configure_settings.snacks)):
                self.snack_boxes.append(tk.IntVar(value=snack_checked))
                self.create_checkbox(frame, anchor='center', text=snack, var=self.snack_boxes[idx])

    def configure_games(self, frame: tk.Frame) -> None:
        tk.Label(frame, text='Amount of Games', font=font.Font(size=9, underline=True)).pack(padx=10, pady=0, anchor='w')

        # use default settings or previously entered settings
        if Configure.configure_settings is None or Configure.configure_settings.num_games == 1:
            self.games = EntryWithPlaceholder(frame, placeholder="1")
        else:
            self.games = EntryWithPlaceholder(frame, placeholder='1', text=Configure.configure_settings.num_games)
        self.games.pack(padx=12, pady=0, anchor='w')

    def configure_resolutions(self, frame: tk.Frame) -> None:
        tk.Label(frame, text='Resolution', font=font.Font(size=9, underline=True)).pack(padx=10, pady=0, anchor='w')
        available_resolutions = ['800x600', '1280x800']
        self.resolutions = ttk.Combobox(frame, value=available_resolutions, width=16, state='readonly')
        self.resolutions.pack(padx=(12, 18))

        # use default settings or previously entered settings
        if Configure.configure_settings is None:
            self.resolutions.current(0)
        else:
            self.resolutions.current(available_resolutions.index(Configure.configure_settings.resolution))

    def create_checkbox(self, master: tk.Frame, *, anchor: str, text: str, var: tk.IntVar) -> None:
        checkbutton = tk.Checkbutton(master, text=text, variable=var, pady=0)
        checkbutton.pack(padx=10, anchor=anchor)

    def start(self) -> None:
        # get selections on location
        locations = tuple(var.get() for var in self.location_boxes)

        # get selections on snack
        snacks = tuple(var.get() for var in self.snack_boxes)

        # get number of games
        num_games = None
        games = self.games.get()
        if games == '':
            num_games = 1
        else:
            try:
                num_games = max(1, int(games))
            except ValueError:
                num_games = 1

        # get resolution
        resolution = self.resolutions.get()
        Configure.configure_settings = ConfigureSettings(locations=locations, snacks=snacks, num_games=num_games, resolution=resolution)

        try:
            self.destroy()
        except Exception:
            pass

class Playing(tk.Tk):
    def __init__(self, resolution: str, num_games: int, current_game: int) -> None:
        width, height = separate(resolution, delimiter='x')
        super().__init__()
        self.title('W101 Pet Dance')
        self.geometry(f"300x130+{width}+{int(height) // 10 * 7}")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        for i in range(3):
            self.rowconfigure(i, weight=1)
        self.bind('q', lambda key: self.stop())
        self.protocol("WM_DELETE_WINDOW", lambda: self.stop())

        # adding frames to window
        frame_top = create_frame(self)
        frame_middle = create_frame(self)
        frame_bottom = create_frame(self)

        # placing in grid
        frame_top.grid(row=0, column=0, sticky='nesw')
        frame_middle.grid(row=1, column=0, sticky='nesw')
        frame_bottom.rowconfigure(0, weight=1)
        frame_bottom.columnconfigure(0, weight=1)
        frame_bottom.columnconfigure(1, weight=1)
        frame_bottom.grid(row=2, column=0, sticky='nesw')

        padx = 16
        self.progress_bar = ttk.Progressbar(frame_middle, orient='horizontal', mode='determinate', length=300-2*padx)
        self.progress_bar.grid(columnspan=3, padx=padx, pady=0)

        self.label = ttk.Label(frame_top, text=self.update_progress_label(), font=font.Font(size=12, weight='bold'))
        self.label.grid(columnspan=3, padx=padx, pady=(10, 0))

        # for bottom frame
        games_progress = ttk.Label(frame_bottom, text=f"Game {current_game + 1} of {num_games}", font=font.Font(size=11, weight='bold'))
        games_progress.grid(row=0, column=0, padx=padx, pady=(0, 10), sticky='w')

        caption = ttk.Label(frame_bottom, text="(press 'q' to quit)")
        caption.grid(row=0, column=1, padx=padx, pady=(0, 10), sticky='w')

        # for self.interval_update()
        self.prev = 0
        self.finished = False

    def update_progress_label(self) -> str:
        #print('updating progress label')
        return f"Current Progress: {self.progress_bar['value']}%"

    def progress(self) -> None:
        #print('updating progress bar')
        if self.progress_bar['value'] < 100:
            self.progress_bar['value'] += 20
            self.label['text'] = self.update_progress_label()
        if self.progress_bar['value'] == 100:
            self.finished = True

    def stop(self) -> None:
        #print('stopping script, calling self.destroy()')
        try:
            # since self.progress() might call self.stop() before self.check_progress_thread() does
            # thus we would be attempting to update a label that is already destroyed
            self.label['text'] = self.update_progress_label()
            self.destroy()
        except Exception:
            pass

    def start_progress_thread(self, thread: threading.Thread) -> None:
        self.after(1000, lambda: self.check_progress_thread(thread))

    def check_progress_thread(self, thread: threading.Thread) -> None:
        if thread.is_alive() and not Globals.q_pressed:
            self.interval_update()
            self.after(200, lambda: self.check_progress_thread(thread))
        else:
            print('thread is dead - progress bar stopped (thread)')
            self.stop()

    def interval_update(self) -> None:
        if DG.turn <= 5:
            if DG.turn != self.prev:
                # new round
                self.progress()
                self.prev += 1