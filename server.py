import socket
import threading
import queue
import time

from desktop_notifier import DesktopNotifier, DesktopNotifierSync

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


class Wettkampf:
    name: str
    official: bool
    lastEditedTime: time.struct_time
    poison = False

    def __init__(self, name, official, poison):
        self.name = name
        self.official = official
        self.poison = poison
        self.lastEditedTime = time.localtime(time.time())

    def computeTime(self):
        return str(self.lastEditedTime.tm_hour) + ":" + str(self.lastEditedTime.tm_min) + ":" + str(self.lastEditedTime.tm_sec)

    def updateTime(self):
        self.lastEditedTime = time.localtime(time.time())

wettkampf_dictionaries = dict[str, Wettkampf]()

global notificationHandler
notificationQueue = queue.Queue[Wettkampf]()


def checkingSocket():
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
    for x in splitNewLine:
        if x == "":  # .split bei NewLine splittet auch das letzte zeichen weg
            continue
        if x == "HI":
            print("HI")
            wettkampf_dictionaries.clear()
            continue
        splitString = x.split("|")
        if len(splitString) == 2:
            if splitString[0] not in wettkampf_dictionaries:
                if splitString[1] == "offiziell":
                    newWettkampf = Wettkampf(splitString[0], True, False)
                else:
                    newWettkampf = Wettkampf(splitString[0], False, False)
                wettkampf_dictionaries[splitString[0]] = newWettkampf # in dict hinzufügen
            else:
                if splitString[1] == "offiziell":
                    wettkampf_dictionaries[splitString[0]].official = True
                else:
                    wettkampf_dictionaries[splitString[0]].official = False

            wettkampf_dictionaries[splitString[0]].updateTime()
            notificationQueue.put(wettkampf_dictionaries[splitString[0]])

        else:
            print("wrong message from client: <" + decodeString + ">")
            continue
    printAll()


def printAll():
    wettkampf_dictionaries_sorted = {k: v for k, v in sorted(wettkampf_dictionaries.items(), key=lambda item: item[0])}
    print("----------")
    for x in wettkampf_dictionaries_sorted:
        wettkampf = wettkampf_dictionaries_sorted[x]
        if wettkampf.official:
            message = wettkampf.name + " offiziell ✔ " + wettkampf.computeTime()
        else:
            message = wettkampf.name + " inoffiziell 𐄂 " + wettkampf.computeTime()
        print(message)
    print("----------")


def notificationWorkerRun():
    notifier = DesktopNotifierSync(app_name="EasyStatus")
    while True:
        work = notificationQueue.get()
        if work.poison:
            break

        if work.official:
            message = work.name + " offiziell ✔"
        else:
            message = work.name + " inoffiziell 𐄂"

        notifier.send(title="Neuen WK:", message=message)


def createNotificationThread():
    global notificationHandler
    notificationHandler = threading.Thread(target=notificationWorkerRun)
    notificationHandler.start()


if __name__ == "__main__":
    print("starting Server...")
    print(HOST + ":" + str(PORT))
    createNotificationThread()
    try:
        checkingSocket()
    except KeyboardInterrupt:
        print("shutting down ...")
        notificationQueue.put(Wettkampf(None, False, True))
        notificationHandler.join()
