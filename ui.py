import tkinter as tk
from tkinter import ttk

class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.debug_mode = True
        self.season = tk.StringVar(self.root, value='current')
        self.race = tk.StringVar(self.root, value='last')
        self.tweet_text_replacement = ""

    def set_options(self, debug_mode, tweet_text_replacement):
        self.root.destroy()
        self.debug_mode = debug_mode
        self.tweet_text_replacement = tweet_text_replacement.strip()

    def launch_ui(self):
        self.root.geometry("600x180")
        self.root.title('Options')
        self.root.resizable(True, True)

        # configure the grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)

        season_label = ttk.Label(self.root, text="Season:")
        season_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        season_entry = ttk.Entry(self.root, textvariable=self.season)
        season_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)

        race_label = ttk.Label(self.root, text="Race:")
        race_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        race_entry = ttk.Entry(self.root, textvariable=self.race)
        race_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)

        tweet_text_label = ttk.Label(self.root, text="Tweet Text:")
        tweet_text_label.grid(column=0, row=2, sticky=tk.NW, padx=5, pady=5)
        tweet_text_entry = tk.Text(self.root, height=4, width=65, )
        tweet_text_entry.grid(column=1, row=2, sticky=tk.E, padx=5, pady=5)

        debug_button = ttk.Button(
            self.root, 
            text='Debug', 
            command=lambda: self.set_options(True, tweet_text_entry.get(1.0, tk.END))
        )
        debug_button.grid(column=0, row=3, sticky=tk.E, padx=5, pady=5)

        publish_button = ttk.Button(
            self.root, 
            text='Publish Results', 
            command=lambda: self.set_options(False, tweet_text_entry.get(1.0, tk.END))
        )
        publish_button.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)

        self.root.mainloop()