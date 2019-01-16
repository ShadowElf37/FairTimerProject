from time import time, sleep
import datetime
from threading import Thread
from tkinter import *
from tkinter import filedialog
from sys import exit
import audio

# Read Config
configfile = 'config'
queue = open(configfile, 'r').read().split('\n')
log = open('log', 'a')


def get_time(sec=True):
    return str(datetime.datetime.now().strftime('%I:%M'+('.%S' if sec else '')+'%p').lower())
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

def sec_to_hms(sec):
    m = sec // 60
    h = m // 60
    s = sec % 60
    return '%s:%s.%s' % (h,m,s)


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
            if self.get_time() <= tc.time:
                self.timed_cmds.remove(tc)
                return tc.text

        return False

    def get_time(self):
        return self.t - (time() - self.start)


    def timed_command(self, time_left, text):
        self.timed_cmds.append(TimedCommand(parse_hms(time_left), text))

    def get_time_str(self):
        return sec_to_hms(round(self.get_time()))

class DeadTimer:
    def __init__(self):
        self.returned = False
        self.returnval = False
        self.start = -1
        self.specialtext = 'Loading...'

    def tick(self):
        return False

    def get_time(self):
        return 0

    def get_time_str(self):
        return self.specialtext

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
            self.returnval = self.get_time()
            return True
        return False

    def get_time(self):
        return time() - self.start

    def get_time_str(self):
        return sec_to_hms(round(self.get_time()))

    def stop(self):
        self.returned = True
        log.write('Timer '+prompt+' - Stopped at' + str(time() - self.start)+', '+timestamp())


current_timer = DeadTimer()
prompt = 'Ready.'
i = 0

root = Tk()
width = 1000
height = 700
root.geometry('%sx%s'%(width,height))
root.title('Mr. Fair\'s Super Special Timer')
root.configure(background='black')

time_label = Label(root, fg='white', bg='black', font=('Helvetica', 50))
time_label.place(x=width/15, y=height/10)
config_file_label = Label(root, fg='white', bg='black', font=('Helvetica', 26))
config_file_label.place(x=width/15, y=height/10*3)
prompt_label = Label(root, fg='#F31', bg='black', font=('Helvetica', 50))
prompt_label.place(x=width/15, y=height/10*4)
timer_label = Label(root, fg='#0FF', bg='black', font=('Helvetica', 80))
timer_label.place(x=width/15, y=height/10*5)
timer_type_label = Label(root, fg='white', bg='black', font=('Helvetica', 20))
timer_type_label.place(x=width/7, y=height/10*6.2)

while True:
    sleep(0.01)
    time_label.configure(text=get_time().replace('am', ' AM').replace('pm', ' PM'))
    config_file_label.configure(text='Loaded: '+configfile)
    prompt_label.configure(text=prompt)
    timer_label.configure(text=current_timer.get_time_str())
    timer_type_label.configure(text='Counting down.' if isinstance(current_timer, Countdown) else 'Counting up.' if isinstance(current_timer, Countup) else 'Holding.')
    try:
        root.update()
        root.update_idletasks()

        if isinstance(current_timer, DeadTimer):
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
                current_timer.specialtext = c[1]
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
                Thread(target=audio.play_wav, args=(f,)).start()

            i += 1

        elif current_timer:
            result = current_timer.tick()
            if result is False:
                continue
            elif result is True:
                rv = current_timer.returnval
                if rv is not 1:
                    log.write(timestamp()+' - '+prompt+' - %d' % rv)
                current_timer = DeadTimer()
            else:
                current_timer.returnval = False
                c = result.split(' ')
                if c[0] == 'prompt':
                    prompt = c[1][c[1].find('"')+1:c[1].find('"', c[1].find('"')+1)]
                    print('$ prompt changed:', prompt)
                
                elif c[0] == 'play':
                    print('$ played sound')
                    f = c[1][c[1].find('"'):c[1].find('"', c[1].find('"')+1)]
                    Thread(target=audio.play_wav, args=(f,)).start()

    except (KeyboardInterrupt, SystemExit, TclError):
        print('Application destroyed.')
        break

# root.destroy()
print('Process complete.')
exit(0)
