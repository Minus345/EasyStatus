import socket
import sys

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

# TODO: geht bestimmt auch schöner
wettkampf_dictionaries = {
    "WK 0": "test"
}


def checkingSocket():
    global serverSocket
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((HOST, PORT))
        serverSocket.listen()

        while True:
            conn, addr = serverSocket.accept()
            print(f"Connected by {addr}")
            try:
                while True:
                    data = conn.recv(1024)
                    # print(data)
                    manageInput(data)
                    if not data:
                        print(f"client {addr} disconnected")
                        break
            except socket.error as e:
                print(f"Socket error occurred")
                sys.exit(1)
            finally:
                conn.close()
                print(f"Connection closed")
    except socket.error as e:
        print(f"Socket error occurred: {e}")
        exit(1)
    except KeyboardInterrupt:
        print(f"Shutting down...")
    finally:
        if 'serverSocket' in globals():
            serverSocket.close()
            print(f"Server socket closed")
        sys.exit(0)


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
