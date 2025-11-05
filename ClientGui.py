from tkinter import *
import socket
import sys
from tkinter import messagebox

clientSocket = socket.socket()

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

root = Tk()

def status_geaendert(status_text, var):
    print(f"{status_text} wurde geändert zu: {'inoffiziell' if var.get() else 'offiziell'}")

    try:
        if var.get() == 1:
            clientSocket.sendall(status_text.encode() + b" | 0")  # 0 ist inoffiziell
        else:
            clientSocket.sendall(status_text.encode() + b" | 1")  # 1 ist offiziell
    except socket.error as e:
        print(f"Error during data exchange: {e}")
        # TODO: Save to file and exit


def openSocket():
    global clientSocket
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            clientSocket.connect((HOST, PORT))
            try:
                clientSocket.sendall(b"Starting...")
            except socket.error as e:
                print(f"Error during data exchange: {e}")
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


def closeSocket():
    clientSocket.close()

def onClose():
    if messagebox.askokcancel("Beenden", "Möchtest du das Fenster wirklich schließen?"):
        # TODO: Save to file
        root.destroy()
        closeSocket()
        sys.exit(0)


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

    # Beispielhafte Liste von Einträgen
    wettkampf_liste = [
        "WK 1",
        "WK 2",
        "WK 3",
        "WK 4",
        "WK 5",
        "WK 6",
        "WK 7"
    ]

    # Jeden Eintrag mit Label und zwei Radiobuttons anzeigen
    for status in wettkampf_liste:
        eintrag_frame = Frame(scrollable_frame, pady=5)
        eintrag_frame.pack(fill=X, padx=10)

        label = Label(eintrag_frame, text=status, width=10, anchor="w")
        label.pack(side=LEFT)

        state = IntVar(value=1)  # Startwert -1 bedeutet "nicht ausgewählt"

        cb1 = Radiobutton(
            eintrag_frame, text="inoffiziell", fg="red", variable=state, value=1,
            command=lambda s=status, v=state: status_geaendert(status, state)
        )
        cb2 = Radiobutton(
            eintrag_frame, text="offiziell", fg="green", variable=state, value=0,
            command=lambda s=status, v=state: status_geaendert(s, v)
        )

        cb1.pack(side=LEFT, padx=5)
        cb2.pack(side=LEFT)

    root.mainloop()


if __name__ == "__main__":
    openSocket()
    createWindow()
