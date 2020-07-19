import threading
import keyboard
import time
import autoit
import FSAFv02b


def main():
    stop_threads = False
    print("Press '.' to start fishing")
    keyboard.wait(".")
    fishing = threading.Thread(target=FSAFv02b.main, args = (1, lambda: stop_threads))
    fishing.start()
    print("///////////////")
    print("Press '.' again to stop fishing")
    keyboard.wait(".")
    stop_threads = True
    fishing.join()


if __name__ == '__main__':
    while True:
        main()