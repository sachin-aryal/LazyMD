# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *

from vmd_runner import run_automation
import threading
import time

win = tk.Tk()

program_title_text = """
 _                     __  __ _____  
| |                   |  \/  |  __ \ 
| |     __ _ _____   _| \  / | |  | |
| |    / _` |_  / | | | |\/| | |  | |
| |___| (_| |/ /| |_| | |  | | |__| |
|______\__,_/___|\__, |_|  |_|_____/ 
                  __/ |              
                 |___/               
"""

program_title = tk.Label(win, text=program_title_text)
program_title["fg"] = "#292B39"
output_box = Listbox(win, height=15)
scrollbar = Scrollbar(win)
# bind output_box to scrollbar
output_box.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=output_box.yview)

submit = tk.Button(win, text="Process", bg="#023D84", fg='white', activebackground="#001C7C",
                   command=lambda: start_process())

browse_file_label = tk.Label(win, text="Select Folder")
output_label = tk.Label(win, text="Program Output")

global_folder = None


def start_process():
    """
    Submit button handler.
    Start the operation of all params are required fieilds are fillted.
    """
    if global_folder is None or global_folder == "":
        messagebox.showerror("Required Field Missing", message="Please select folder")
        return
    try:
        method = run_automation
        th = threading.Thread(target=method, args=(global_folder, output_box,))
        th.start()
        start_button.config(state=DISABLED)
        threading.Thread(target=monitor_thread_status, args=(th, )).start()
    except Exception as ex:
        print(str(ex))
        output_box.insert(END, str(ex))


def monitor_thread_status(th):
    while True:
        if not th.isAlive():
            start_button.config(state=NORMAL)
            break
        time.sleep(2)


def browse_folder():
    """
    Select the source folder for operation.
    """
    global global_folder
    global_folder = filedialog.askdirectory()

start_button = tk.Button(text="Submit", command=start_process)


def create_initial_screen():
    upload_directory = tk.Button(text="Browse Folder", command=browse_folder)
    """
    Add tkinter widgets to window.
    """
    row = 0
    program_title.grid(column=2, row=row, pady=10, sticky=N + S + W + E)
    row += 1
    browse_file_label.grid(column=0, row=row, padx=10, pady=10, sticky=N + S + W + E)
    upload_directory.grid(column=1, row=row, padx=10, pady=10, sticky=N + S + W + E)
    row += 1
    start_button.grid(column=0, row=row, padx=10, pady=10, sticky=N + S + W + E)
    row += 1
    output_label.grid(column=0, row=row, padx=10, pady=10, sticky=N + S + W + E)
    row += 1
    output_box.grid(column=0, row=row, padx=10, pady=10, columnspan=3, sticky=N + S + W + E)


def on_closing():
    """
    Confirmation window before quiting application.
    """
    if messagebox.askokcancel("Exit", "Are you sure ?"):
        win.destroy()
        exit(0)


def main():
    try:
        # Set window size to 480x640
        win.geometry("650x650")
        win.winfo_toplevel().title("LazyMD")
        create_initial_screen()
        win.protocol("WM_DELETE_WINDOW", on_closing)
        win.mainloop()
        win.resizable(False, False)
    except Exception as ex:
        output_box.insert(END, str(ex))


if __name__ == "__main__":
    print(program_title_text)
    main()
