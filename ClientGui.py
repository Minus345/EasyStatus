import os.path
from tkinter import *
import socket
import sys
from tkinter import messagebox
import pickle

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

saveFileExists = False
path = "wk.pkl"

wettkampf_dictionaries = {
    "WK 1": "inoffiziell",
    "WK 2": "inoffiziell",
    "WK 3": "inoffiziell",
    "WK 4": "inoffiziell",
    "WK 5": "inoffiziell",
    "WK 6": "inoffiziell",
    "WK 7": "inoffiziell",
    "WK 8": "inoffiziell",
    "WK 9": "inoffiziell",
    "WK 10": "inoffiziell",
    "WK 11": "inoffiziell",
    "WK 12": "inoffiziell",
    "WK 13": "inoffiziell",
    "WK 14": "inoffiziell",
    "WK 15": "inoffiziell",
}

root = Tk()


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


def openSocket():
    global clientSocket
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((HOST, PORT))
            try:
                clientSocket.sendall(b"HI\n")
                if saveFileExists:
                    print(f"Send all known Data")
                    sendAllKnownData()
            except socket.error as e:
                print(f"Error during data exchange: {e}")
                saveAndExit()
        except socket.timeout:
            print(f"Connection attempt timed out")
            sys.exit(1)
        except ConnectionRefusedError:
            print(f"Connection refused. Make sure the server is running.")
            sys.exit(1)
        except socket.error as e:
            print(f"Connection error: {e}")
            sys.exit(1)
    except socket.error as e:
        print(f"Socket creation error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\nClient shutting down...")
        sys.exit(1)


def saveAndExit():
    closeSocket()
    with open(path, "wb") as f:
        pickle.dump(wettkampf_dictionaries, f)
    root.destroy()
    sys.exit(1)


def loadData():
    global wettkampf_dictionaries
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, "rb") as f:
            wettkampf_dictionaries = pickle.load(f)
            global saveFileExists
            saveFileExists = True
    else:
        print(f"Could´t find save file -> not loading anything")


def closeSocket():
    clientSocket.close()


def onClose():
    if messagebox.askokcancel("Beenden", "Möchtest du das Fenster wirklich schließen?"):
        saveAndExit()


def createWindow():
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

        if saveFileExists:
            if wettkampf_dictionaries[wk] == "inoffiziell":
                state = IntVar(value=1)
            else:
                state = IntVar(value=0)
        else:
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


if __name__ == "__main__":
    loadData()
    openSocket()
    createWindow()
