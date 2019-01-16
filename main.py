from time import time, sleep
import datetime
from threading import Thread
from tkinter import *
from sys import exit

# Read Config
queue = open('config', 'r').read().split('\n')
log = open('log', 'a')


def get_time(sec=True):
    return str(datetime.datetime.now().strftime('%I:%M'+(':%S' if sec else '')+'%p').lower())
def get_date():
    return str(datetime.datetime.now().strftime('%d/%m/%Y'))
def timestamp():
    return str(datetime.datetime.now())

def parse_hms(st):
    h = st.find('h')
    m = st.find('m')
    s = st.find('s')
    hours = minutes = seconds = 0
    if h != -1:
        hours = int(st[:h])
    if m != -1:
        minutes = int(st[h+1:m])
    if s != -1:
        seconds = int(st[max(m,h)+1:s])

    return hours*3600 + minutes*60 + seconds


class TimedCommand:
    def __init__(self, time, cmdtext):
        self.time = time
        self.text = cmdtext

# Countdown timer object
class Countdown:
    def __init__(self, t):
        self.returned = False
        self.returnval = 0
        self.t = t
        self.start = -1
        self.timed_cmds = []

    def tick(self):
        if self.returnval:
            return
        if self.start == -1:
            self.start = time()
        if time() - self.start >= self.t:
            self.returned = True
            self.returnval = 1
            return True

        for tc in self.timed_cmds:
            if self.t - (time() - self.start) <= tc.time:
                self.timed_cmds.remove(tc)
                return tc.text

        return False

    def timed_command(self, time_left, text):
        self.timed_cmds.append(TimedCommand(parse_hms(time_left), text))


# Countup timer object
class Countup:
    def __init__(self):
        self.returned = False
        self.returnval = 0
        self.start = -1

    def tick(self):
        if self.returnval:
            return
        if self.start == -1:
            self.start = time()
        if self.returned:
            self.returnval = time() - self.start
            return True
        return False

    def stop(self):
        self.returned = True
        log.write('Timer '+prompt+' - Stopped at' + str(time() - self.start)+', '+timestamp())


root = Tk()
current_timer = None
prompt = 'Ready.'
i = 0

width = 1000
height = 700
root.geometry('%sx%s'%(width,height))
root.title('Mr. Fair\'s Super Special Timer')
root.configure(background='black')

while True:
    sleep(0.01)
    try:
        root.update()
        root.update_idletasks()

        if current_timer is None:
            try:
                cmd = queue[i]
            except IndexError:
                break

            if not cmd or cmd[0] == '#':
                i += 1
                continue
            c = cmd.split(' ')

            if c[0] == 'await_time':
                print('awaiting', c[1])
                if get_time(sec=False).strip('0') != c[1].strip('0'):
                    continue

            elif c[0] == 'prompt':
                prompt = cmd[cmd.find('"')+1:cmd.find('"', cmd.find('"')+1)]
                print('prompt changed:', prompt)

            elif c[0] == 'countdown': # MUST SET UP
                print('created countdown')
                current_timer = Countdown(parse_hms(c[1]))
                extras = cmd.split('-')[1:]
                for arg in extras:
                    t = arg[:arg.find('(')]
                    s = arg[arg.find('(')+1:arg.find(')', arg.find(')')+1)]
                    
                    current_timer.timed_command(t, s)
                holding = True

            elif c[0] == 'countup':
                print('created countup')
                current_timer = Countup()
                holding = True

            elif c[0] == 'play':
                print('played sound')
                f = cmd[cmd.find('"'):cmd.find('"', cmd.find('"')+1)]

            i += 1

        elif current_timer:
            result = current_timer.tick()
            if result is False:
                continue
            elif result is True:
                rv = current_timer.returnval
                if rv is not 1:
                    log.write(timestamp()+' - '+prompt+' - %d' % rv)
                current_timer = None
            else:
                current_timer.returnval = False
                c = result.split(' ')
                if c[0] == 'prompt':
                    prompt = c[1][c[1].find('"')+1:c[1].find('"', c[1].find('"')+1)]
                    print('$ prompt changed:', prompt)
                
                elif c[0] == 'play':
                    f = c[1][c[1].find('"'):c[1].find('"', c[1].find('"')+1)]
                    print('$ played sound')

    except (KeyboardInterrupt, SystemExit, TclError):
        print('Application destroyed.')
        break

# root.destroy()
print('Process complete.')
exit(0)
