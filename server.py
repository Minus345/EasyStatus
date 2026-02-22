import socket
import sys

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

wettkampf_dictionaries = dict[str, str]()


def checkingSocket():
    #TODO multithreaded mit mehreren clients
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((HOST, PORT))
        serverSocket.listen()

        while True:
            conn, addr = serverSocket.accept()
            print(f"Connected by {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)
                    # print(data)
                    manageInput(data)
                    if not data:
                        print(f"client {addr} disconnected")
                        break

def manageInput(data):
    decodeString = data.decode()

    splitNewLine = decodeString.split("\n")
    # print(splitNewLine)
    for x in splitNewLine:
        if x == "":  # .split bei NewLine splittet auch das letzte zeichen weg
            continue
        if x == "HI":
            print("HI")
            wettkampf_dictionaries.clear()
            continue
        splitString = x.split("|")
        # noinspection PyRedundantParentheses
        if (len(splitString) == 2):
            # print(splitString[0] + " -> " + splitString[1])
            if splitString[0] not in wettkampf_dictionaries:
                wettkampf_dictionaries[splitString[0]] = splitString[1]
            else:
                wettkampf_dictionaries.update({splitString[0]: splitString[1]})
        else:
            print("wrong message from client: <" + decodeString + ">")
            continue
    printAll()


def printAll():
    wettkampf_dictionaries_sorted = {k: v for k, v in sorted(wettkampf_dictionaries.items(), key=lambda item: item[0])}
    print("----------")
    for x in wettkampf_dictionaries_sorted:
        print(x + " " + wettkampf_dictionaries_sorted[x])
    print("----------")


if __name__ == "__main__":
    print("starting Server...")
    print(HOST)
    checkingSocket()
