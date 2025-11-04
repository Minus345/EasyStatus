from tkinter import *
import socket

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server


def status_geaendert(status_text, var):
    print(f"{status_text} wurde geändert zu: {'inoffiziell' if var.get() else 'offiziell'}")

    if var.get() == 1:
        clientSocket.sendall(status_text.encode() + b" | 0")  # 0 ist inoffiziell
    else:
        clientSocket.sendall(status_text.encode() + b" | 1")  # 1 ist offiziell


def openSocket():
    clientSocket.connect((HOST, PORT))
    clientSocket.sendall(b"Starting...")


def closeSocket():
    clientSocket.close()


def createWindow():
    root = Tk()
    root.title("EasyStatus")
    root.geometry("400x370")

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
