from tkinter import *
import socket
import sys
from tkinter import messagebox
import Startup

PORT = 65432  # The port used by the server

wettkampf_dictionaries = dict()

global root
global clientSocket


def status_geaendert(wkNumber, var):
    print(f"{wkNumber} wurde geändert zu: {'inoffiziell' if var.get() else 'offiziell'}")

    if var.get() == 1:
        wettkampf_dictionaries[wkNumber] = "inoffiziell"
    else:
        wettkampf_dictionaries[wkNumber] = "offiziell"
    try:
        clientSocket.sendall(wkNumber.encode() + b"|" + wettkampf_dictionaries[wkNumber].encode() + b"\n")
    except socket.error as e:
        print(f"Error during data exchange: {e}")
        saveAndExit()


def sendAllKnownData():
    try:
        for wk in wettkampf_dictionaries:
            clientSocket.sendall(wk.encode() + b"|" + wettkampf_dictionaries[wk].encode() + b"\n")
            # print("send" + wk)
    except socket.error as e:
        print(f"Error during data exchange: {e}")
        saveAndExit()


def openSocket(host, port):
    global clientSocket
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((host, port))
            try:
                ## send all known data
                clientSocket.sendall(b"HI\n")
                return None
            except socket.error as e:
                print(f"Error during data exchange: {e}")
                saveAndExit()
        except socket.timeout:
            return "Connection attempt timed out"
        except ConnectionRefusedError:
            return "Connection refused. Make sure the server is running."
        except socket.error as e:
            return f"Connection error: {e}"
    except socket.error as e:
        return f"Socket creation error: {e}"
    except KeyboardInterrupt:
        return f"\nClient shutting down..."


def saveAndExit():
    clientSocket.close()
    root.destroy()
    sys.exit(1)


def onClose():
    if messagebox.askokcancel("Beenden", "Möchtest du das Fenster wirklich schließen?"):
        saveAndExit()


def createWindow(filePath):
    global root
    root = Tk()
    root.title("EasyStatus")
    root.geometry("400x370")

    # Close Handler
    root.protocol("WM_DELETE_WINDOW", onClose)

    # Canvas + Scrollbar Setup
    canvas = Canvas(root)
    scrollbar = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Jeden Eintrag mit Label und zwei Radiobuttons anzeigen
    for wk in wettkampf_dictionaries:
        eintrag_frame = Frame(scrollable_frame, pady=5)
        eintrag_frame.pack(fill=X, padx=10)

        label = Label(eintrag_frame, text=wk, width=10, anchor="w")
        label.pack(side=LEFT)

        state = IntVar(value=-1)  # Startwert -1 bedeutet "nicht ausgewählt"

        cb1 = Radiobutton(
            eintrag_frame, text="inoffiziell", fg="red", variable=state, value=1,
            command=lambda s=wk, v=state: status_geaendert(s, v)
        )
        cb2 = Radiobutton(
            eintrag_frame, text="offiziell", fg="green", variable=state, value=0,
            command=lambda s=wk, v=state: status_geaendert(s, v)
        )

        cb1.pack(side=LEFT, padx=5)
        cb2.pack(side=LEFT)

    root.mainloop()


def readFile(filePath):
    if filePath is None:
        messagebox.showerror("Error", "File path cannot be None")
        sys.exit(1)

    try:
        file = open(filePath, "r")
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found")
        sys.exit(1)
    else:
        with file:
            for line in file:
                global wettkampf_dictionaries
                wettkampf_dictionaries[line.split(":")[0]] = line.split(":")[1]


if __name__ == "__main__":
    port, ipaddress, filePath = Startup.startUp(PORT)
    error = openSocket(ipaddress, port)
    readFile(filePath)
    if error is not None:
        messagebox.showinfo(title="Connection Error", message=error)
        sys.exit(1)
    createWindow(filePath)
