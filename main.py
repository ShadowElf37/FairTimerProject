from time import time, sleep
import datetime
from threading import Thread
from tkinter import *
from tkinter import filedialog
from sys import exit
import os
import audio
from traceback import format_exc
from math import floor
from fractions import Fraction

project_dir = os.getcwd()
showfiles = project_dir+'\\ShowFiles\\'
ico = project_dir+'\\bin\\favicon.ico'

FONT = 'Helvetica'

# Read Config
root = Tk()
root.title('temp')
root.withdraw()
configfile = filedialog.askopenfilename(initialdir=showfiles, title="Select config file",
                                                 filetypes=(("config files", "*.cfg"), ("all files", "*.*")))
root.destroy()
    #f = param_entry.get()#'default_config.cfg'
queue = open(configfile, 'r').read().split('\n')
audiofolder = default_audiofolder = showfiles+'audio\\'


def get_time(sec=True):
    return str(datetime.datetime.now().strftime('%I:%M'+('.%S' if sec else '')+'%p').lower())
def get_date():
    return str(datetime.datetime.now().strftime('%d/%m/%Y'))
def timestamp():
    now = str(datetime.datetime.now())
    return now[:now.find('.')]

log = open('ShowFiles\\logs\\log_'+timestamp().replace(':', ';')+'.log', 'a')

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
    return '%02d:%02d.%02d' % (h,m,s)


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
            self.start = floor(time())
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
            return self.t - (floor(time()) - self.start)
        return self.t - self.pause_time + self.start

    def pause(self):
        self.pause_time = floor(time())

    def unpause(self):
        self.start += floor(time()) - self.pause_time

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
            self.start = round(time())
            self.pause_time = self.start
        if self.returned:
            self.returnval = self.get_time()
            return True
        return False

    def pause(self):
        self.pause_time = floor(time())

    def unpause(self):
        self.start += floor(time()) - self.pause_time

    def get_time(self):
        global paused
        if not paused:
            return floor(time()) - self.start
        return floor(self.pause_time) - self.start

    def get_time_str(self):
        return sec_to_hms(self.get_time())

    def stop(self):
        self.returned = True
        # "Act 2" - Stopped at 1 hour 12 minutes, 2019-01-19 17:38
        sec = round(self.get_time())
        ms = str(sec - self.get_time())[1:3]
        m = sec // 60
        h = m // 60
        h = h % 24
        m = m % 60
        s = sec % 60
        log.write(('"'+prompt+'" - Stopped at %s hours, %s minutes, and %s%s seconds on ' % (h,m,s,ms)) + timestamp() + '. Line %s.\n' % i)


current_timer = DeadTimer()
prompt = 'No prompt set yet.'
i = 0
paused = False
skipped = False

root = Tk()
root.iconbitmap(ico)

width = 1000
height = 700
# root = Toplevel(base_root)
root.geometry('%sx%s'%(width,height))
root.title('Stage Timer')
root.configure(background='black')
root.focus_force()


time_label_fs = 50
prompt_label_fs = 50
timer_label_fs = 160
config_file_label_fs = 14
timer_type_label_fs = 20

time_label = Label(root, fg='#0F0', bg='black', font=(FONT, time_label_fs))
time_label.place(relx=1/2, rely=3/20, anchor=CENTER)
prompt_label = Label(root, fg='#F00', bg='black', font=(FONT, 50))
prompt_label.place(relx=1/2, rely=7/10, anchor=CENTER)
timer_label = Label(root, fg='#02F', bg='black', font=(FONT, 160))
timer_label.place(relx=1/2, rely=9/20, anchor=CENTER)
config_file_label = Label(root, fg='white', bg='black', font=(FONT, 16))
config_file_label.place(relx=1/2, rely=8/10, anchor=CENTER)
timer_type_label = Label(root, fg='white', bg='black', font=(FONT, 20))
timer_type_label.place(relx=1/2, rely=12/20, anchor=CENTER)


fullscreen = False
alt_tabbed = False
old_window_pos = root.winfo_x(), root.winfo_y()

def alt_tab(*args):
    global alt_tabbed, fullscreen
    if fullscreen:
        alt_tabbed = True
        toggle_fullscreen()

def toggle_fullscreen(*args):
    global root, fullscreen, old_window_pos, alt_tabbed
    if not fullscreen:
        old_window_pos = root.winfo_x(), root.winfo_y()
        root.geometry('{}x{}+0+0'.format(root.winfo_screenwidth(), root.winfo_screenheight()))
        root.overrideredirect(1)  # borderless
        fullscreen = True
    elif alt_tabbed:
        root.overrideredirect(0)
        alt_tabbed = False
    else:
        root.geometry('{}x{}+{}+{}'.format(width, height, *old_window_pos))
        root.overrideredirect(0)
        root.focus_force()
        fullscreen = False
root.bind('<F5>', toggle_fullscreen)
root.bind('<Alt_L>', alt_tab)
root.bind('<Win_L>', alt_tab)


def load_cfg():
    global configfile, queue, i, current_timer
    temp = configfile
    configfile = filedialog.askopenfilename(initialdir=showfiles, title="Select file",
                                               filetypes=(("cfg files", "*.cfg"), ("all files", "*.*")))
    #configfile = param_entry.get()
    if not configfile:
        configfile = temp
    current_timer = DeadTimer()
    i = 0
    queue = open(configfile, 'r').read().split('\n')
    configfile = configfile.split('/')[-1]
    print('cfg file set')

def switch_logfile():
    global log
    temp = log.name
    log.close()
    f = filedialog.askopenfilename(initialdir=showfiles, title="Select file",
                                                 filetypes=(("log files", "*.log"), ("all files", "*.*")))
    #f = param_entry.get()
    if not f:
        log = open(temp, 'a')
        return
    log = open(f, 'a')
    print('log file set')

def find_audio():
    global audiofolder
    audiofolder = filedialog.askdirectory()
    if not audiofolder:
        audiofolder = default_audiofolder
        return
    print('audio folder set')

def pause():
    global paused, current_timer
    paused = True
    current_timer.pause()

def resume():
    global paused, current_timer, skipped
    paused = False
    current_timer.unpause()
    skipped = False

def skip():
    global i, current_timer, paused, skipped
    paused = False
    skipped = True
    if isinstance(current_timer, DeadTimer): i += 1
    current_timer = DeadTimer()

def stop():
    global current_timer, paused, i
    paused = False
    current_timer.stop()
    current_timer = DeadTimer()


button_width = 10
load_cfg_button_fs = 8
pause_button_fs = skip_button_fs = 18

load_cfg_button = Button(root, text="Load Show", font=(FONT, 8), width=button_width, command=load_cfg)
load_cfg_button.place(relx=1/2, rely=17/20, anchor=CENTER)
#check_logs_button = Button(root, text="Set Log", font=(FONT, 18), width=bw, command=switch_logfile)
#check_logs_button.place(x=width/8*6, y=height/11*5, anchor=CENTER)
#find_audio_button = Button(root, text="Find Audio", font=(FONT, 18), width=bw, command=find_audio)
#find_audio_button.place(x=width/8*6, y=height/11*1, anchor=CENTER)
pause_button = Button(root, text="Pause", font=(FONT, 18), width=button_width)
pause_button.place(relx=2/3, rely=9/10, anchor=CENTER)
skip_button = Button(root, text="Skip", font=(FONT, 18), width=button_width)
skip_button.place(relx=1/3, rely=9/10, anchor=CENTER)

# param_entry = Entry(root, width=30, font=('Lucida Console', 14))
# param_entry.place(x=width/8*6, y=height/11*10, anchor=CENTER)
# param_entry.insert(0, 'Enter file names here')

f5_label = Label(text='F5 - Fullscreen', font=('Helvetica', 20), bg='#000', fg='#151515')
f5_label.place(relx=1, rely=0, anchor=NE)
f5_label.bind("<Button-1>", lambda *args: f5_label.place_forget())
f5_label.bind("<Button-2>", lambda *args: f5_label.place_forget())

fair_img = PhotoImage(file=project_dir+'\\bin\\favicon.ppm')
fair_img_label1 = Label(image=fair_img, width=194, height=194)
fair_img_label2 = Label(image=fair_img, width=194, height=194)
#fair_img_label1.place(relx=0, rely=0, anchor=NW)
#fair_img_label2.place(relx=1, rely=0, anchor=NE)
fair_hidden = True

def toggle_fair_img(*args):
    global root, fair_img_label1, fair_img_label2, fair_hidden
    if not fair_hidden:
        fair_hidden = True
        fair_img_label1.place_forget()
        fair_img_label2.place_forget()
    else:
        fair_hidden = False
        fair_img_label1.place(relx=0, rely=0, anchor=NW)
        fair_img_label2.place(relx=1, rely=0, anchor=NE)
root.bind('<Key-f>', lambda *x: root.bind('<Key-a>', lambda *x: root.bind('<Key-i>', lambda *x: root.bind('<Key-r>', lambda *x: root.bind('<Key-period>', toggle_fair_img)))))


error_msg = None
def error_msg_close():
    global error_msg
    error_msg.destroy()
    root.focus_force()
    error_msg = None


def window_close(*args):
    root.destroy()
    log.close()
    print('Application exited by user.')
    exit(0)
root.protocol("WM_DELETE_WINDOW", window_close)

old_wh_dif = 1,1
while True:
    try:
        sleep(0.02)

        w = root.winfo_width()
        h = root.winfo_height()
        hdif = h/height
        wdif = w/width
        fac = min(hdif, wdif) * 1.0 + max(hdif, wdif) * 0.0

        time_label.config(font=(FONT, int(time_label_fs*fac)))
        prompt_label.config(font=(FONT, int(prompt_label_fs * fac)))
        timer_label.config(font=(FONT, int(timer_label_fs * fac)))
        config_file_label.config(font=(FONT, int(config_file_label_fs * fac)))
        timer_type_label.config(font=(FONT, int(timer_type_label_fs * fac)))

        load_cfg_button.config(font=(FONT, int(load_cfg_button_fs * fac)), width=int(button_width))# * fac))
        skip_button.config(font=(FONT, int(skip_button_fs * fac)), width=int(button_width))# * fac))
        pause_button.config(font=(FONT, int(pause_button_fs * fac)), width=int(button_width))# * fac))

        if old_wh_dif != (hdif, wdif) and not fair_hidden:  # Zoom/subsample are really expensive functions for some reason, so the less we have to run them, the better
            ffac = Fraction(fac).limit_denominator(19)
            tempimg = fair_img.zoom(ffac.numerator).subsample(ffac.denominator)
            fair_img_label1.config(image=tempimg, width=int(194*fac), height=int(194*fac))
            fair_img_label2.config(image=tempimg, width=int(194*fac), height=int(194*fac))

            old_wh_dif = hdif, wdif


        time_label.configure(text=get_time().replace('am', ' AM').replace('pm', ' PM'))
        config_file_label.configure(text='Show: '+configfile.split('/')[-1])
        prompt_label.configure(text=prompt)
        timer_label.configure(text=current_timer.get_time_str())
        timer_type_label.configure(text=('Counting down.' if isinstance(current_timer, Countdown) else 'Counting up.' if isinstance(current_timer, Countup) else 'Holding.'))# + ' (Line %s)' % i)
        skip_button.configure(text='Skip', command=skip)
        if isinstance(current_timer, Countup):
            skip_button.configure(text='Stop', command=stop)
        pause_button.configure(text='Pause', command=pause)
        if skipped and not isinstance(current_timer, DeadTimer) and not paused:
            pause()
        if skipped and not isinstance(current_timer, DeadTimer):
            pause_button.configure(text='Start', command=resume)
        elif paused and not skipped:
            pause_button.configure(text='Resume', command=resume)


        fps = 24
        root.update()
        root.update_idletasks()
        if error_msg:
            error_msg.update()
            error_msg.update_idletasks()

        if isinstance(current_timer, DeadTimer):
            try:
                cmd = queue[i]
            except IndexError:
                break

            if not cmd or cmd[0] == '#':
                i += 1
                #print('@', i)
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

            elif c[0] == 'countdown':
                print('created countdown')
                current_timer = Countdown(parse_hms(c[1]))
                extras = cmd.split('$')[1:]
                oskipped = skipped
                skipped = True
                for arg in extras:
                    if arg.find('(') != -1:
                        t = arg[:arg.find('(')]
                        s = arg[arg.find('(')+1:arg.find(')', arg.find(')')+1)]
                        if arg.count(')') > 1:
                            raise SyntaxError('You forgot a $ in your timed commands on line %d' % (i+1))
                        current_timer.timed_command(t, s)
                    else:
                        if arg.strip() == 'auto':
                            if not oskipped:
                                skipped = False
                holding = True

            elif c[0] == 'countup':
                print('created countup')
                current_timer = Countup()
                holding = True
                opts = cmd.split('$')[1:]
                oskipped = skipped
                skipped = True
                for opt in opts:
                    if opt.strip() == 'auto':
                        if not oskipped:
                            skipped = False

            elif c[0] == 'play':
                print('played sound')
                f = audiofolder+cmd[cmd.find('"')+1:cmd.find('"', cmd.find('"')+1)]
                Thread(target=audio.play_wav, args=(f,)).start()

            else:
                raise SyntaxError('This config line may be invalid: "'+cmd+'"')

        elif current_timer:
            result = current_timer.tick()
            if result is False:
                continue
            elif result is True:
                rv = current_timer.returnval
                current_timer = DeadTimer()
            else:
                current_timer.returnval = False
                c = result.split(' ')
                if c[0] == 'prompt':
                    prompt = result[result.find('"')+1:result.find('"', result.find('"')+1)]
                    print('$ prompt changed:', prompt)
                
                elif c[0] == 'play':
                    print('$ played sound')
                    f = audiofolder+result[result.find('"')+1:result.find('"', result.find('"')+1)]
                    Thread(target=audio.play_wav, args=(f,)).start()

            continue

    except (KeyboardInterrupt, SystemExit, TclError):
        print('Application destroyed.')
        break

    except Exception as e:
        error_msg = Tk()
        error_msg.protocol("WM_DELETE_WINDOW", error_msg_close)
        error_msg.focus()
        error_msg.title('Mr. Fair\'s Super Special ERROR')
        error = Label(error_msg,
                      text='An error occurred!\nMake sure your config files are in order.\nIf the problem persists, contact Yovel and send him a screenshot so he can investigate the issue.\n\n'+format_exc(),
                      fg="red", font=('Lucida Console', 12))
        error.pack()

    i += 1
    #print(i)

# root.destroy()
print('Process complete.')
log.close()
exit(0)
