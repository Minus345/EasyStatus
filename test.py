import signal
import sys
from threading import Thread
from time import sleep


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def thread():
    while True:
        try:
            line = input()
        except:
            print('interupedt')
            break
        print(line)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    thread = Thread(target=thread)
    thread.start()
    print('Press Ctrl+C')
    while True:
        sleep(1)