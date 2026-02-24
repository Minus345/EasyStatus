import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def onClose():
    root.destroy()
    sys.exit(0)

root = tk.Tk()
# Close Handler
root.protocol("WM_DELETE_WINDOW", onClose)
root.title("Easy Status - Startup")

ip_var = tk.StringVar()
port_var = tk.StringVar()

def __start_action():
    root.destroy()


def startUp(defaultPort: int):
    port_var.set(str(defaultPort))
    tk.Label(root, text="Server IP Address:").grid(row=0, column=0, sticky="e")
    tk.Entry(root, textvariable=ip_var, width=25).grid(row=0, column=1)

    tk.Label(root, text="Port:").grid(row=1, column=0, sticky="e")
    tk.Entry(root, textvariable=port_var, width=10).grid(row=1, column=1, sticky="w")

    tk.Button(root, text="Start", width=20, command=__start_action).grid(row=3, column=0, columnspan=3, pady=10)

    root.mainloop()

    ip = ip_var.get()
    port = int(port_var.get())
    return port, ip
