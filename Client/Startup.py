import tkinter as tk
from tkinter import filedialog, messagebox

root = tk.Tk()
root.title("Easy Status - Startup")

ip_var = tk.StringVar()
port_var = tk.StringVar()
file_var = tk.StringVar()


def open_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        file_var.set(filepath)


def __start_action():
    root.destroy()


def startUp(defaultPort: int):
    port_var.set(str(defaultPort))
    tk.Label(root, text="IP Address:").grid(row=0, column=0, sticky="e")
    tk.Entry(root, textvariable=ip_var, width=25).grid(row=0, column=1)

    tk.Label(root, text="Port:").grid(row=1, column=0, sticky="e")
    tk.Entry(root, textvariable=port_var, width=10).grid(row=1, column=1, sticky="w")

    tk.Label(root, text="File:").grid(row=2, column=0, sticky="e")
    tk.Entry(root, textvariable=file_var, width=25).grid(row=2, column=1)
    tk.Button(root, text="Open File", command=open_file).grid(row=2, column=2, padx=5)

    tk.Button(root, text="Start", width=20, command=__start_action).grid(row=3, column=0, columnspan=3, pady=10)

    root.mainloop()

    ip = ip_var.get()
    port = int(port_var.get())
    file = file_var.get()
    return port, ip, file
