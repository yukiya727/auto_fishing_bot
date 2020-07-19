import time
import os
import sys
import keyboard
import autoit
from ctypes import windll

timeBeginPeriod = windll.winmm.timeBeginPeriod
timeBeginPeriod(1)


def openfile(dname, fname):
    global steps
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    directory = 'recorder_files'
    try:
        session_name = dname
    except:
        print('you must enter a name for the session\nfor example: python replay.py session_name')
        sys.exit()
    dir_path = os.path.join(os.getcwd(), directory, session_name)

    file_name = fname
    file_path = os.path.join(dir_path, file_name)

    # open the recording file
    with open(file_path, 'r') as f:
        steps = f.readlines()


SpecialKeys = [
    "ctrl", "alt", "shift", "win"
]


def Keystring(str):
    global k, key_type

    def ifcontrolkey(dkey):
        global key_type
        if any(c in dkey for c in SpecialKeys):
            key_type = key_type.strip(" ")
        return dkey

    if k:
        k = False
        str = ifcontrolkey(str)
        return "{0}{1}{2}{3}".format("{", str, key_type, "}")
    if str.find("keypressed") != -1:
        k = True
        key_type = " down"
    if str.find("keyreleased") != -1:
        k = True
        key_type = " up"
    return str


def load_replay():
    global k

    new_steps = []
    temp_step = []
    k_last = ""
    temp_step = ""
    skip = False
    pause = False
    startcount = False
    t_last = 0.0
    t_temp = 0.0
    lag_limit = 144
    id = 0

    lag_limit = 1 / lag_limit

    for step in steps:
        new_step = []
        k = False

        for i in step.split(','):
            # Reformat key string
            if i.find("Key.") != -1:
                i = i.replace("Key.", "")
            if i.find("Button.") != -1:
                i = i.replace("Button.", "")
            if i.find("'") != -1:
                i = i.replace("'", "")

            i = i.lower()
            i = Keystring(i)

            if i == k_last:
                skip = True
                break
            if i.find("{") != -1:
                k_last = i
            skip = False

            new_step.append(i.strip('\n'))

        if skip:
            continue

        if not startcount:
            if new_step[0] != 'start':
                t_last = float(new_step[-1])
            if new_step[0] == 'start':
                startcount = True
                continue
            continue

        if new_step[0] == 'mousemove' and id != 0:
            if new_steps[id - 1][0] == 'mousemove':
                if float(new_step[-1]) - t_last < lag_limit:
                    temp_step = new_step
                    t_temp = float(new_step[-1])
                    pause = True
                    continue
            t_last = float(new_step[-1])

        elif new_step[0] != 'mousemove' and id > 1:
            if new_steps[id - 1][0] == 'mousemove' and new_steps[id - 2][0] == 'mousemove' and pause == True:
                new_steps.append(temp_step)
                t_last = t_temp

        elif id == 0:
            t_last = float(new_step[-1])

        new_steps.append(new_step)
        pause = False
        id += 1
    # for item in new_steps:
    #     print(item)
    print("Recorded objects:", len(new_steps))
    # print(new_steps[0][-1])
    return new_steps, float(new_steps[0][-1])


def play(log, speed, tlast, debug_mode):
    st = 0.0
    tlast -= 0.01

    if debug_mode:
        timer = time.perf_counter()
    offset_timer = time.perf_counter()

    for step in log:
        if step[0] == 'mousemove':
            t_offset = time.perf_counter() - offset_timer - st
            # print(t_offset)
            st = (float(step[-1]) - tlast - t_offset) / speed
            # print(st)
            offset_timer = time.perf_counter()
            if st > 0:
                time.sleep(st)
            autoit.mouse_move(int(step[1]), int(step[2]), 0)
            tlast = float(step[-1])
            continue

        if step[0] == 'mousepressed':
            t_offset = time.perf_counter() - offset_timer - st
            st = (float(step[-1]) - tlast - t_offset) / speed
            offset_timer = time.perf_counter()
            if st < 0.0:
                time.sleep(st)
            autoit.mouse_move(int(step[2]), int(step[3]), 0)
            autoit.mouse_down(step[1])
            tlast = float(step[-1])
            continue

        if step[0] == 'mousereleased':
            t_offset = time.perf_counter() - offset_timer - st
            st = (float(step[-1]) - tlast - t_offset) / speed
            offset_timer = time.perf_counter()
            if st < 0.0:
                time.sleep(st)
            autoit.mouse_move(int(step[2]), int(step[3]), 0)
            autoit.mouse_up(step[1])
            tlast = float(step[-1])
            continue

        if step[0] == 'mousescrolled':
            t_offset = time.perf_counter() - offset_timer - st
            st = (float(step[-1]) - tlast - t_offset) / speed
            offset_timer = time.perf_counter()
            if st > 0:
                time.sleep(st)
            autoit.mouse_wheel(int(step[2]), int(step[3]), 0)
            autoit.mouse_up(step[1])
            tlast = float(step[-1])
            continue

        if step[0] == 'keypressed':
            t_offset = time.perf_counter() - offset_timer - st
            # print(t_offset)
            st = (float(step[-1]) - tlast - t_offset) / speed
            offset_timer = time.perf_counter()
            if st > 0:
                time.sleep(st)
            autoit.send(step[1])
            tlast = float(step[-1])
            continue

        if step[0] == 'keyreleased':
            t_offset = time.perf_counter() - offset_timer - st
            st = (float(step[-1]) - tlast - t_offset) / speed
            offset_timer = time.perf_counter()
            if st > 0:
                time.sleep(st)
            autoit.send(step[1])
            tlast = float(step[-1])
            continue

        if step[0] == 'done':
            print('End playing')
            if debug_mode:
                print(time.perf_counter() - timer)
            pass


# This makes the program asking for the file name every single time you open the program
# file_name = input("Please specify the text file you want to replay from:")
# file_name = "history" + file_name + ".txt"
# Alternatively you can add the line below to replace the input command
def main():
    file_name = "history.txt"
    openfile("pynput_record", file_name)
    l1, t1 = load_replay()
    file_name = "history1.txt"
    openfile("pynput_record", file_name)
    l2, t2 = load_replay()
    file_name = "history2.txt"
    openfile("pynput_record", file_name)
    l3, t3 = load_replay()
    # print("Ready, press '.' to start")
    # keyboard.wait(".")
    play(l1, 1, t1, True)
    play(l2, 1, t2, True)
    play(l3, 1, t3, True)
    autoit.mouse_wheel("down", 30)
    autoit.mouse_click_drag(950, 470, 950, 475, button="right", speed=100)
    autoit.mouse_click_drag(950, 475, 965, 475, button="right", speed=50)