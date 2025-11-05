import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

# TODO: geht bestimmt auch schöner
wettkampf_dictionaries = {
    "WK 0": "test"
}


# TODO: Fehlerbehandlung
def checkingSocket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    # print(data)
                    manageInput(data)
                    if not data:
                        print(f"client {addr} disconnected")
                        break
                    ##conn.sendall(data)


def manageInput(data):
    decodeString = data.decode()
    # noinspection PyRedundantParentheses
    if (decodeString == "Starting..."):
        print("Client Starting")
        return
    splitString = decodeString.split("|")
    # noinspection PyRedundantParentheses
    if (len(splitString) == 2):
        # print(splitString[0] + " -> " + splitString[1])
        if splitString[0] not in wettkampf_dictionaries:
            wettkampf_dictionaries[splitString[0]] = splitString[1]
        else:
            wettkampf_dictionaries.update({splitString[0]: splitString[1]})
    else:
        print("wrong message from client")
        return
    printAll()


def printAll():
    print("----------")
    for x in wettkampf_dictionaries:
        print(x + " " + wettkampf_dictionaries[x])
    print("----------")


if __name__ == "__main__":
    print("starting Server...")
    checkingSocket()
