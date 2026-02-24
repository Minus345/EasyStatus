import socket
import sys
import signal
import threading
import queue
import time

from desktop_notifier import DesktopNotifier, DesktopNotifierSync

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


class Wettkampf:
    name: str
    official: bool
    lastEditedTime: time.struct_time
    poison = False
    protokoll = False
    urkunden = False
    ausgehangen = False

    def __init__(self, name, official, poison):
        self.name = name
        self.official = official
        self.poison = poison
        self.lastEditedTime = time.localtime(time.time())

    def computeTime(self):
        if self.lastEditedTime.tm_hour < 10:
            hour = str(self.lastEditedTime.tm_hour) + " "
        else:
            hour = str(self.lastEditedTime.tm_hour)

        if self.lastEditedTime.tm_min < 10:
            mins = str(self.lastEditedTime.tm_min) + " "
        else:
            mins = str(self.lastEditedTime.tm_min)

        return hour + ":" + mins

    def updateTime(self):
        self.lastEditedTime = time.localtime(time.time())


wettkampf_dictionaries = dict[str, Wettkampf]()
dict_lock = threading.Lock()

global notificationHandler
notificationQueue = queue.Queue[Wettkampf]()

global userInputThread


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

    # TODO: kleinerer kritischer abschnitt

    with dict_lock:
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
                    wettkampf_dictionaries[splitString[0]] = newWettkampf  # in dict hinzufügen
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
    with dict_lock:
        wettkampf_dictionaries_sorted = {k: v for k, v in
                                         sorted(wettkampf_dictionaries.items(), key=lambda item: item[0])}
    longestName = 0
    for x in wettkampf_dictionaries_sorted:
        if len(wettkampf_dictionaries_sorted[x].name) > longestName:
            longestName = len(wettkampf_dictionaries_sorted[x].name)
    print("+-" + longestName * "-" + "-+---------------+[Time]-+[P]+[A]+[U]+")

    for x in wettkampf_dictionaries_sorted:
        wettkampf = wettkampf_dictionaries_sorted[x]

        bufferSpacesCount = longestName - len(wettkampf_dictionaries_sorted[x].name)
        bufferSpaces = " " * bufferSpacesCount

        if wettkampf.protokoll:
            p = "✔"
        else:
            p = "𐄂"
        if wettkampf.ausgehangen:
            a = "✔"
        else:
            a = "𐄂"
        if wettkampf.urkunden:
            u = "✔"
        else:
            u = "𐄂"
        wkParms = wettkampf.computeTime() + " | " + p + " | " + a + " | " + u + " |"

        if wettkampf.official:
            message = "| " + wettkampf.name + bufferSpaces + " | offiziell   ✔ | " + wkParms
        else:
            message = "| " + wettkampf.name + bufferSpaces + " | inoffiziell 𐄂 | " + wkParms
        print(message)

    print("+-" + longestName * "-" + "-+---------------+-------+---+---+---+")


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
    notificationHandler = threading.Thread(target=notificationWorkerRun, daemon=True)
    notificationHandler.start()


def wrongInput():
    print("wrong format: add/rem <name> p/u/a")


def userInputThreadRun():
    while True:
        print("running")
        try:
            line = input()
        except:
            print("interupted")
            return

        splitLine = line.split(" ")

        if len(splitLine) != 3:
            wrongInput()
            continue

        selectedWk = splitLine[1]

        # o = unset
        # 1 = True
        # -1 = False
        p = 0
        u = 0
        a = 0

        match splitLine[0]:
            case "add":
                match splitLine[2]:
                    case "p":
                        p = 1
                    case "u":
                        u = 1
                    case "a":
                        a = 1
                    case _:
                        wrongInput()
                        continue
            case "rem":
                match splitLine[2]:
                    case "p":
                        p = -1
                    case "u":
                        u = -1
                    case "a":
                        a = -1
                    case _:
                        wrongInput()
                        continue
            case _:
                wrongInput()
                continue

        if setWk(selectedWk, u, p, a):
            printAll()
            continue
        else:
            print("can not find wk")


def setWk(selectedWk: str, u: int, p: int, a: int) -> bool:
    with dict_lock:
        for x in wettkampf_dictionaries:
            thisWk = wettkampf_dictionaries[x]
            if thisWk.name == selectedWk:
                if p != 0:
                    if p == 1:
                        thisWk.protokoll = True
                    else:
                        thisWk.protokoll = False
                if u != 0:
                    if u == 1:
                        thisWk.urkunden = True
                    else:
                        thisWk.urkunden = False
                if a != 0:
                    if a == 1:
                        thisWk.ausgehangen = True
                    else:
                        thisWk.ausgehangen = False
                return True
    return False


def createUserInputThread():
    global userInputThread
    userInputThread = threading.Thread(target=userInputThreadRun, daemon=True)
    userInputThread.start()


if __name__ == "__main__":
    print("starting Server...")
    signal.signal(signal.SIGINT, signal_handler)
    print(HOST + ":" + str(PORT))
    createNotificationThread()
    createUserInputThread()
    try:
        checkingSocket()
    except KeyboardInterrupt:
        sys.exit(0)
