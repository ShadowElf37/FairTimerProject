from time import time, sleep
import datetime
from threading import Thread
from tkinter import *
from tkinter import filedialog
from sys import exit
import audio

# Read Config
configfile = filedialog.askopenfilename(initialdir="ShowFiles/", title="Select config file",
                                                 filetypes=(("config files", "*.cfg"), ("all files", "*.*")))
    #f = param_entry.get()#'default_config.cfg'
queue = open(configfile, 'r').read().split('\n')
audiofolder = 'ShowFiles/audio/'


def get_time(sec=True):
    return str(datetime.datetime.now().strftime('%I:%M'+(':%S' if sec else '')+'%p').lower())
def get_date():
    return str(datetime.datetime.now().strftime('%d/%m/%Y'))
def timestamp():
    return str(datetime.datetime.now())

log = open('ShowFiles/logs/log_'+timestamp()+'.log', 'a')

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
    h = h % 24
    m = m % 60
    s = sec % 60
    return '%02d:%02d:%02d' % (h,m,s)


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
        self.pause_time = -1

    def tick(self):
        if self.returnval:
            return
        if self.start == -1:
            self.start = round(time())
            self.pause_time = self.start
        if time() - self.start >= self.t and not paused:
            self.returned = True
            self.returnval = 1
            return True

        for tc in self.timed_cmds:
            if self.get_time() <= tc.time:
                self.timed_cmds.remove(tc)
                return tc.text

        return False

    def get_time(self):
        global paused
        if not paused:
            return self.t - (time() - self.start)
        return self.t - self.pause_time + self.start

    def pause(self):
        self.pause_time = time()

    def unpause(self):
        self.start += time() - self.pause_time

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
    def pause(self):
        pass
    def unpause(self):
        pass

# Countup timer object
class Countup:
    def __init__(self):
        self.returned = False
        self.returnval = 0
        self.start = -1
        self.pause_time = -1
        self.unpause_time = -1

    def tick(self):
        if self.returnval:
            return
        if self.start == -1:
            self.start = time()
            self.pause_time = self.start
        if self.returned:
            self.returnval = self.get_time()
            return True
        return False

    def pause(self):
        self.pause_time = time()

    def unpause(self):
        self.start += time() - self.pause_time

    def get_time(self):
        global paused
        if not paused:
            return time() - self.start
        return self.pause_time - self.start

    def get_time_str(self):
        return sec_to_hms(round(self.get_time()))

    def stop(self):
        self.returned = True
        log.write('Timer with prompt "'+prompt+'" - Stopped at ' + str(round(self.get_time(), 2))+', '+timestamp()+'; line %s\n' % i)


current_timer = DeadTimer()
prompt = 'No prompt set yet.'
i = 0
paused = False

root = Tk()
width = 1000
height = 700
root.geometry('%sx%s'%(width,height))
root.title('Mr. Fair\'s Super Special Timer')
root.configure(background='black')

time_label = Label(root, fg='#0F0', bg='black', font=('Helvetica', 50))
time_label.place(x=width/15, y=height/10)
config_file_label = Label(root, fg='white', bg='black', font=('Helvetica', 26))
config_file_label.place(x=width/15, y=height/10*3)
prompt_label = Label(root, fg='#F00', bg='black', font=('Helvetica', 50))
prompt_label.place(x=width/15, y=height/10*4)
timer_label = Label(root, fg='#02F', bg='black', font=('Helvetica', 80))
timer_label.place(x=width/15, y=height/10*6)
timer_type_label = Label(root, fg='white', bg='black', font=('Helvetica', 20))
timer_type_label.place(x=width/14, y=height/10*5.7)


def load_cfg():
    global configfile, queue, i, current_timer
    current_timer = DeadTimer()
    i = 0
    configfile = filedialog.askopenfilename(initialdir="ShowFiles/", title="Select file",
                                               filetypes=(("cfg files", "*.cfg"), ("all files", "*.*")))
    #configfile = param_entry.get()
    queue = open(configfile, 'r').read().split('\n')
    configfile = configfile.split('/')[-1]
    print('cfg file set')

def switch_logfile():
    global log
    log.close()
    f = filedialog.askopenfilename(initialdir="ShowFiles/", title="Select file",
                                                 filetypes=(("log files", "*.log"), ("all files", "*.*")))
    #f = param_entry.get()
    log = open(f, 'a')
    print('log file set')

def find_audio():
    global audiofolder
    audiofolder = filedialog.askdirectory()
    print('audio folder set')

def pause():
    global paused, current_timer
    paused = True
    current_timer.pause()

def resume():
    global paused, current_timer
    paused = False
    current_timer.unpause()

def skip():
    global i, current_timer, paused
    paused = False
    if isinstance(current_timer, DeadTimer): i += 1
    current_timer = DeadTimer()

def stop():
    global current_timer, paused, i
    paused = False
    current_timer.stop()
    current_timer = DeadTimer()

bw = 10
load_cfg_button = Button(root, text="Load Config", font=('Helvetica', 18), width=bw, command=load_cfg)
load_cfg_button.place(x=width/8*6, y=height/11*3, anchor=CENTER)
check_logs_button = Button(root, text="Set Log", font=('Helvetica', 18), width=bw, command=switch_logfile)
check_logs_button.place(x=width/8*6, y=height/11*5, anchor=CENTER)
find_audio_button = Button(root, text="Find Audio", font=('Helvetica', 18), width=bw, command=find_audio)
find_audio_button.place(x=width/8*6, y=height/11*1, anchor=CENTER)
pause_button = Button(root, text="Pause", font=('Helvetica', 18), width=bw)
pause_button.place(x=width/8*6, y=height/11*7, anchor=CENTER)
skip_button = Button(root, text="Skip", font=('Helvetica', 18), width=bw)
skip_button.place(x=width/8*6, y=height/11*9, anchor=CENTER)

# param_entry = Entry(root, width=30, font=('Lucida Console', 14))
# param_entry.place(x=width/8*6, y=height/11*10, anchor=CENTER)
# param_entry.insert(0, 'Enter file names here')

while True:
    sleep(0.01)
    time_label.configure(text=get_time().replace('am', ' AM').replace('pm', ' PM'))
    config_file_label.configure(text='Loaded: '+configfile)
    prompt_label.configure(text=prompt)
    timer_label.configure(text=current_timer.get_time_str())
    timer_type_label.configure(text=('Counting down.' if isinstance(current_timer, Countdown) else 'Counting up.' if isinstance(current_timer, Countup) else 'Holding.') + ' (Line %s)' % i)
    skip_button.configure(text='Skip', command=skip)
    if isinstance(current_timer, Countup):
        skip_button.configure(text='Stop', command=stop)
    pause_button.configure(text='Pause', command=pause)
    if paused:
        pause_button.configure(text='Resume', command=resume)
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
                extras = cmd.split('$')[1:]
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
                f = audiofolder+cmd[cmd.find('"'):cmd.find('"', cmd.find('"')+1)]
                Thread(target=audio.play_wav, args=(f,)).start()

            i += 1

        elif current_timer:
            result = current_timer.tick()
            if result is False:
                continue
            elif result is True:
                rv = current_timer.returnval
                #if rv is not 1:
                #    log.write('\n'+timestamp()+' - '+prompt+' - %d' % rv)
                current_timer = DeadTimer()
            else:
                current_timer.returnval = False
                c = result.split(' ')
                if c[0] == 'prompt':
                    prompt = c[1][c[1].find('"')+1:c[1].find('"', c[1].find('"')+1)]
                    print('$ prompt changed:', prompt)
                
                elif c[0] == 'play':
                    print('$ played sound')
                    f = audiofolder+c[1][c[1].find('"'):c[1].find('"', c[1].find('"')+1)]
                    Thread(target=audio.play_wav, args=(f,)).start()

    except (KeyboardInterrupt, SystemExit, TclError):
        print('Application destroyed.')
        break

# root.destroy()
print('Process complete.')
log.close()
exit(0)
