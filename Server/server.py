import socket
import sys
import signal
import threading
import queue
import time
from time import sleep

from desktop_notifier import DesktopNotifier, DesktopNotifierSync

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
FILE_PATH = ""
SLEEP_SAVE_MINUTES = 10


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    saveFile()
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
global saveThread


def checkingSocket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        # wenn fehler einfach crashen lassen
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((HOST, PORT))
        serverSocket.listen()
        serverSocket.settimeout(1.0)

        while True:
            try:
                conn, addr = serverSocket.accept()
            except socket.timeout:
                continue
            except socket.error as e:
                print("socket error accept: " + str(e))
                continue
            print(f"Connected by {addr}")
            with conn:
                conn.settimeout(1.0)
                # connection inti -> send all known data
                sendString = ""
                for x in wettkampf_dictionaries:
                    thisWk = wettkampf_dictionaries[x]
                    sendString += thisWk.name + ":" + str(thisWk.official) + "\n"
                sendString += "ende\n"

                try:
                    conn.sendall(sendString.encode())
                except socket.error as e:
                    print("socket error send: " + str(e))
                    continue

                # main rec loop
                while True:
                    try:
                        data = conn.recv(1024)
                    except socket.timeout:
                        continue
                    except socket.error as e:
                        print("socket error accept: " + str(e))
                        break

                    if not data:
                        print(f"client {addr} disconnected")
                        break
                    manageInput(data)


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
                continue
            splitString = x.split(":")
            if len(splitString) == 2:
                if splitString[0] not in wettkampf_dictionaries:
                    if splitString[1] == "True":
                        newWettkampf = Wettkampf(splitString[0], True, False)
                    elif splitString[1] == "False":
                        newWettkampf = Wettkampf(splitString[0], False, False)
                    else:
                        print("wrong message from client: <" + decodeString + ">")
                        continue
                    wettkampf_dictionaries[splitString[0]] = newWettkampf  # in dict hinzufügen
                else:
                    if splitString[1] == "True":
                        wettkampf_dictionaries[splitString[0]].official = True
                    elif splitString[1] == "False":
                        wettkampf_dictionaries[splitString[0]].official = False
                    else:
                        print("wrong message from client: <" + decodeString + ">")
                        continue

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


def wrongInput():
    print("wrong format: add/rem <name> p/u/a")


def userInputThreadRun():
    while True:
        try:
            line = input()
        except:
            print("interupted")
            return

        match line:
            case "s":
                saveFile()
                continue
            case "p":
                printAll()
                continue

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


def readFile():
    # TODO: check file suffix
    try:
        file = open(FILE_PATH, "r")
    except FileNotFoundError:
        print("File not found")
        sys.exit(1)
    with (file):
        counter = 0
        with dict_lock:
            global wettkampf_dictionaries
            for line in file:
                counter += 1
                line = line.rstrip("\n")
                split = line.split(":")
                print(split)
                try:
                    wettkampf_dictionaries[split[0]] = Wettkampf(split[0], readBool(split[1]), False)
                    wettkampf_dictionaries[split[0]].protokoll = readBool(split[2])
                    wettkampf_dictionaries[split[0]].ausgehangen = readBool(split[3])
                    wettkampf_dictionaries[split[0]].urkunden = readBool(split[4])

                except IndexError:
                    print("File Reading Error in line:[ " + str(counter) + " ] " + line)


def readBool(string: str) -> bool:
    if string == "True":
        return True
    else:
        return False


def saveFile():
    print("saving file")
    try:
        file = open(FILE_PATH, "w")
    except FileNotFoundError:
        print("File not found")
        sys.exit(1)
    with file:
        with dict_lock:
            for x in wettkampf_dictionaries:
                wk = wettkampf_dictionaries[x]
                print(
                    wk.name + ":" + str(wk.official) + ":" + str(wk.protokoll) + ":" + str(wk.ausgehangen) + ":" + str(
                        wk.urkunden), file=file)


def saveThreadRun():
    while True:
        saveFile()
        sleep(SLEEP_SAVE_MINUTES * 60)


if __name__ == "__main__":
    print("reading startup arguments....")
    try:
        FILE_PATH = sys.argv[1]
        HOST = sys.argv[2]
        if len(sys.argv) > 3:
            PORT = int(sys.argv[3])
    except (IndexError, ValueError):
        print("usage: < python3 server.py FILE_PATH HOST PORT > port is optional")
        sys.exit(1)
    print("path: " + FILE_PATH + " - " + HOST + ":" + str(PORT))

    print("starting server...")
    signal.signal(signal.SIGINT, signal_handler)
    readFile()
    printAll()

    userInputThread = threading.Thread(target=userInputThreadRun, daemon=True)
    userInputThread.start()

    notificationHandler = threading.Thread(target=notificationWorkerRun, daemon=True)
    notificationHandler.start()

    saveThread = threading.Thread(target=saveThreadRun, daemon=True)
    saveThread.start()

    try:
        checkingSocket()
    except KeyboardInterrupt:
        print("keyboard interrupt")
        saveFile()
        sys.exit(0)
