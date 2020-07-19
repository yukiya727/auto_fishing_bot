import time
import os
import sys
import keyboard
import pynput.mouse
import pynput.keyboard


def on_move(x, y):
    global file_path, no_lag_mode, acc_lag, lag
    print('MouseMove,{0},{1},{2}'.format(
        x, y, time.perf_counter()))
    with open(file_path, 'a') as f:
        if no_lag_mode:
            pass
        else:
            f.write('MouseMove,{0},{1},{2}'.format(
                x, y, time.perf_counter()))
            f.write('\n')


def on_click(x, y, button, pressed):
    global file_path, no_lag_mode, acc_lag, lag
    print('{0},{1},{2},{3},{4}'.format(
        'MousePressed' if pressed else 'MouseReleased', button, x, y, time.perf_counter()))
    with open(file_path, 'a') as f:
        if no_lag_mode:
            acc_lag += lag
            f.write('{0},{1},{2},{3},{4}'.format(
                'MousePressed' if pressed else 'MouseReleased', button, x, y, acc_lag))
            f.write('\n')
        else:
            f.write('{0},{1},{2},{3},{4}'.format(
                'MousePressed' if pressed else 'MouseReleased', button, x, y, time.perf_counter()))
            f.write('\n')


def on_scroll(x, y, dx, dy):
    global file_path, no_lag_mode, acc_lag, lag
    print('MouseScrolled,{0},{1},{2}'.format(
        x, y, time.perf_counter()))
    with open(file_path, 'a') as f:
        if no_lag_mode:
            acc_lag += lag
            f.write('MouseScrolled,{0},{1},{2}'.format(
                x, y, acc_lag))
            f.write('\n')
        else:
            f.write('MouseScrolled,{0},{1},{2}'.format(
                x, y, time.perf_counter() ))
            f.write('\n')


def on_press(key):
    global file_path, no_lag_mode, acc_lag, lag
    try:
        print('KeyPressed,{0},{1}'.format(
            key.char, time.perf_counter()))
        with open(file_path, 'a') as f:
            if no_lag_mode:
                acc_lag += lag
                f.write('KeyPressed,{0},{1}'.format(
                    key.char, acc_lag))
                f.write('\n')
            else:
                f.write('KeyPressed,{0},{1}'.format(
                    key.char, time.perf_counter() ))
                f.write('\n')
    except AttributeError:
        print('KeyPressed,{0},{1}'.format(
            key, time.perf_counter()))
        with open(file_path, 'a') as f:
            if no_lag_mode:
                acc_lag += lag
                f.write('KeyPressed,{0},{1}'.format(
                    key, acc_lag))
                f.write('\n')
            else:
                f.write('KeyPressed,{0},{1}'.format(
                    key, time.perf_counter()))
                f.write('\n')


def on_release(key):
    global file_path, no_lag_mode, acc_lag, lag

    print('KeyReleased,{0},{1}'.format(
        key, time.perf_counter()))
    with open(file_path, 'a') as f:
        f.write('KeyReleased,{0},{1}'.format(
            key, time.perf_counter()))
        f.write('\n')

    if key == pynput.keyboard.Key.f10:
        with open(file_path, 'a') as f:
            f.write('done')
        # Stop listener
        if debug_mode:
            print("Time elapesed recording:", (time.perf_counter() - timer))
        pynput.mouse.Listener.stop(m_listener)
        print("recorder stopped")
        # And just to get rid of the last two recorded key actions
        with open(file_path, 'r') as f:
            lines = f.readlines()
        with open(file_path, 'w') as f:
            for _ in range(2):
                del lines[-2]
            for line in lines:
                f.write(line)
        return False
    if key == pynput.keyboard.Key.f8:
        with open(file_path, 'a') as f:
            f.write('start')
            f.write('\n')


os.chdir(os.path.dirname(os.path.realpath(__file__)))
directory = 'recorder_files'
try:
    session_name = "pynput_record"
except:
    print('you must enter a name for the session\nfor example: python record.py session_name')
    sys.exit()
dir_path = os.path.join(os.getcwd(), directory, session_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
file_name = 'history'
i = 1
while os.path.isfile(dir_path + '/' + file_name + '.txt'):
    file_name = 'history'
    file_name += str(i)
    i += 1
file_name += '.txt'

print("The recorded actions will be saved in:", dir_path)
print("With the file named:", file_name)
file_path = os.path.join(dir_path, file_name)

debug_mode = False
no_lag_mode = False

# mode = input("Turn on no lag mode?(y/n) ")
mode = "n"
if "y" in mode:
    no_lag_mode = True
    if "-debug" in mode:
        debug_mode = True

print("Please press 'F8' key to start recording")
keyboard.wait("F8")
timer = time.perf_counter()
acc_lag = timer
lag = 0.1

with pynput.keyboard.Listener(
        on_press=on_press,
        on_release=on_release
) as k_listener, \
        pynput.mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as m_listener:
    k_listener.join()
    m_listener.join()
