import socket
import sys
import Startup
from tkinter import *
from tkinter import messagebox

PORT = 65432  # The port used by the server

wettkampf_dictionaries = dict[str, bool]()

global root
global clientSocket


def status_geaendert(wkNumber, var):
    if var.get() == 1:
        wettkampf_dictionaries[wkNumber] = True  # offiziell
    else:
        wettkampf_dictionaries[wkNumber] = False  # inoffiziell
    try:
        clientSocket.sendall((wkNumber + ":" + str(wettkampf_dictionaries[wkNumber]) + "\n").encode())
    except socket.error as e:
        print(e)

        # Try to Reconnect to Server
        errorString = "Error during data exchange: " + str(e) + " Trying reconnect:"
        while True:
            doReconnect = messagebox.askyesno("Error", errorString)
            if doReconnect:
                errorSock = openSocket(ipaddress, port)
                if errorSock is None:
                    root.destroy()
                    createWindow()
                    break
                errorString = "Error during connection to Server: " + ipaddress + " : " + str(
                    port) + " -> " + errorSock + " Trying reconnect: "
            else:
                root.destroy()
                sys.exit(1)


def openSocket(host: str, port: int):
    global clientSocket
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
    except socket.timeout:
        return "Connection attempt timed out"
    except ConnectionRefusedError:
        return "Connection refused. Make sure the server is running."
    except socket.error as e:
        return f"Connection error: {e}"
    except KeyboardInterrupt:
        return f"\nClient shutting down..."

    clientSocket.settimeout(1.0)

    # send start
    try:
        clientSocket.sendall(b"HI\n")
    except socket.error as e:
        return f"Error during data exchange (send): {e}"

    # get all known data
    data = ""
    while True:
        try:
            revBytes = clientSocket.recv(1024)
        except socket.error as e:
            return f"Error during data exchange (recv): {e}"
        data += revBytes.decode()
        if data.find("ende\n") != -1:
            break

    splitLine = data.split("\n")
    for line in splitLine:
        if line == "ende":
            break
        splitName = line.split(":")
        if splitName[1] == "True":
            wettkampf_dictionaries[splitName[0]] = True
        elif splitName[1] == "False":
            wettkampf_dictionaries[splitName[0]] = False
        else:
            return "wrong message rev: " + line
    return None


def onClose():
    if messagebox.askokcancel("Beenden", "Möchtest du das Fenster wirklich schließen?"):
        clientSocket.close()
        sys.exit(1)


def createWindow():
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

        if wettkampf_dictionaries[wk]:
            state = IntVar(value=1)  # offiziell
        else:
            state = IntVar(value=0)  # inoffiziell

        cb1 = Radiobutton(
            eintrag_frame, text="inoffiziell", fg="red", variable=state, value=0,
            command=lambda s=wk, v=state: status_geaendert(s, v)
        )
        cb2 = Radiobutton(
            eintrag_frame, text="offiziell", fg="green", variable=state, value=1,
            command=lambda s=wk, v=state: status_geaendert(s, v)
        )

        cb1.pack(side=LEFT, padx=5)
        cb2.pack(side=LEFT)

    root.mainloop()


if __name__ == "__main__":
    port, ipaddress = Startup.startUp(PORT)
    error = openSocket(ipaddress, port)
    if error is not None:
        messagebox.showinfo(title="Error", message=error)
        sys.exit(0)
    createWindow()
