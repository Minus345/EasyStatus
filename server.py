import socket
from base64 import decode
from email.base64mime import decodestring

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

wettkampf_liste = [
    "WK 1",
    "WK 2",
    "WK 3",
    "WK 4",
    "WK 5",
    "WK 6",
    "WK 7"
]


def checkingSocket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    print(data)
                    manageInput(data)
                    if not data:
                        print(f"client {addr} disconnected")
                        break
                    ##conn.sendall(data)


def manageInput(data):
    decodeString = data.decode()
    splitString = decodeString.split("|")


if __name__ == "__main__":
    print("starting Server...")
    checkingSocket()
