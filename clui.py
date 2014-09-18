import sys, re
import threading
from getpass import getpass
from time import sleep
import curses, curses.panel
from curses.textpad import rectangle
from lib.textpad import CustomTextbox

from lib.async import CallEvery, CallLater, loop, close_all, _tasks, asyncfreq
from lib.eventgenlib import create_splunk_input, connect_to_splunk

import splunklib.client as client

class EventGenCLI(object):
    simspd = 0.2
    cluispd = 0.2
    sock = None
    tcpinput = None
    service = None
    loops = []
    freq = 1
    rr = 50
    loop = None
    config = None
    thread = None
    text = []
    output_length = 15
    latency = False

    def __init__(self, CONFIG, ver):
        self.config = CONFIG
        self.thread = threading.Thread(target=self.asyncThread)
        self.ver = ver

    def output(self, text, newline=True):
        if len(self.text) == self.output_length:
            self.text.pop(0)
        self.text.append(text)

    def login(self):
        print 'Splunk Login:'
        user = raw_input('Username: ')
        password = getpass()
        print 'connecting to', self.config['host']+':'+str(self.config['splunk_rest_port'])
        try:
            self.service = connect_to_splunk(self.config, user, password)
        except client.AuthenticationError:
            print "login failed"
            sys.exit()
        self.sock, self.tcpinput = create_splunk_input(self.service, self.config)

    def startCases(self):
        for c in self.config['cases'].keys():
            self.output(' '.join(['starting:', c]))
            loop = CallEvery(self.freq,
                        self.config['cases'][c]['callback'],
                        sock=self.sock,
                        name=c,
                        output=self.output,
                        config=self.config['cases'][c],
                        commands={},
                        )
            loop._target.regen(self.rr)
            self.loops.append(loop)

    def start(self):
        self.thread = threading.Thread(target=self.asyncThread)
        self.thread.start()

    def make_panel(self, stdscr, h,w, y,x, str, normal=True):
        win = curses.newwin(h,w, y,x)
        panel = curses.panel.new_panel(win)
        panel.top()
        win.erase()
        if normal:
            win.box()
            win.addstr(1, 2, str)
        return win, panel

    def place_text(self, win, text, lines):
        yoffset = 3
        for line in range(lines):
            if len(text) <= line:
                win.addstr(line+yoffset, 2, "")    
            else:
                # trim lines to length of window
                t = text[line][0:win.getmaxyx()[1]-3]
                win.addstr(line+yoffset, 2, t)

    def simspd_popup(self, stdscr, error=False):
        """ simulation speed (not working) """
        h,w = stdscr.getmaxyx()
        win, panel = self.make_panel(stdscr, 2,10, h/2,w/2, "Frequency\n", normal=False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        win.bkgd(' ', curses.color_pair(1))

        text = CustomTextbox(win)
        curses.panel.update_panels(); stdscr.refresh()
        result = text.edit()
        try:
            asyncfreq = float(result)
            self.output('set simspd to: %s' % asyncfreq)
        except ValueError:
            self.simspd_popup(stdscr, error=True)

    def cluispd_popup(self, stdscr, error=False):
        """ curses update speed Input """
        h,w = stdscr.getmaxyx()
        win, panel = self.make_panel(stdscr, 2,10, h/2,w/2, "Frequency\n", normal=False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        win.bkgd(' ', curses.color_pair(1))

        text = CustomTextbox(win)
        curses.panel.update_panels(); stdscr.refresh()
        result = text.edit()
        try:
            self.cluispd = float(result)
            self.output('set cluispd to: %s' % result)
        except ValueError:
            self.cluispd_popup(stdscr, error=True)

    def rr_popup(self, stdscr, error=False):
        """ Responce Chance Input """
        h,w = stdscr.getmaxyx()
        win, panel = self.make_panel(stdscr, 4,20, h/2,w/2, "Response Chance\n", normal=False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        win.bkgd(' ', curses.color_pair(1))
        y,x = win.getyx()
        win.addstr(y,x, "must be 0-100:\n")

        text = CustomTextbox(win)
        curses.panel.update_panels(); stdscr.refresh()
        result = text.edit()
        try:
            result = ''.join(x for x in result.split(':')[-1] if x.isdigit())
            r = float(result)
            if not r>=0 or not r<=100:
                raise ValueError('must be between 0 and 100')
            self.set_rr(r)
            self.output('set response chance to: %s' % result)
        except ValueError:
            self.rr_popup(stdscr, error=True)

    def freq_popup(self, stdscr, error=False):
        """ Frequency Input """
        h,w = stdscr.getmaxyx()
        win, panel = self.make_panel(stdscr, 2,10, h/2,w/2, "Frequency\n", normal=False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        win.bkgd(' ', curses.color_pair(1))

        text = CustomTextbox(win)
        curses.panel.update_panels(); stdscr.refresh()
        result = text.edit()
        try:
            self.set_freq(float(result))
            self.output('set freq to: %s' % result)
        except ValueError:
            self.freq_popup(stdscr, error=True)

    def config_popup(self, stdscr):
        """ Config Menu """
        h,w = stdscr.getmaxyx()
        win_conf, panel_conf = self.make_panel(stdscr, 15,40, 4,w/3, "Config")
        win_conf.hline(2,1,'-',win_conf.getmaxyx()[1]-2)
        sy,sx = win_conf.getyx()
        sh,sw = win_conf.getmaxyx()
        win_conf.hline(sh-4,1,'-',sw-2)
        win_conf.addstr(sh-3, sx+1, "(q)uit  (f)req  (r)esponse chance")
        win_conf.addstr(sh-2, sx+1, "(l)atency  (c)lui-speed  (s)im speed")
                           #y  #x
        win_conf.addstr(sh/2-4, 2, "sim speed: %.2f" % asyncfreq)
        win_conf.addstr(sh/2-3, 2, "clui speed: %.2f" % self.cluispd)
        win_conf.addstr(sh/2-2, 2, "frequency: %.2f" % self.freq)
        win_conf.addstr(sh/2-1, 2, "response chance: %d" % self.rr)
        win_conf.addstr(sh/2,   2, "latency: %s" % (self.latency and "Enabled" or "Disabled"))

        curses.panel.update_panels(); stdscr.refresh()
        
        stdscr.nodelay(0)
        key = stdscr.getch()
        stdscr.nodelay(1)

        if key == ord('q'):
            return
        elif key == ord('f'):
            self.freq_popup(stdscr)
        elif key == ord('r'):
            self.rr_popup(stdscr)
        elif key == ord('l'):
            if self.latency:
                self.output('stopping latency')
                self.stop_latency()
            else:
                self.output('starting latency')
                self.start_latency()
        elif key == ord('c'):
            self.cluispd_popup(stdscr)
        elif key == ord('s'):
            self.simspd_popup(stdscr)

        self.config_popup(stdscr)

    def app(self, stdscr):
        """ Main Menu / Log Viewer """
        curses.curs_set(0)
        #curses.cbreak()
        stdscr.nodelay(1)
        stdscr.box()
        stdscr.addstr(2, 2, "EventGen (%s)     (q)uit  (c)onfig" % self.ver)
        h,w = stdscr.getmaxyx()

        win_log = None
        panel_log = None
        while True:
            key = stdscr.getch()
            if key is None:
                pass
            elif key == ord('q'):
                break
            elif key == ord('c'):
                self.config_popup(stdscr)
                panel_log.top()

            win_log, panel_log = self.make_panel(stdscr, h-5,w-8, 4,4, "Log")
            win_log.hline(2,1,'-',win_log.getmaxyx()[1]-2)
            self.place_text(win_log, self.text, self.output_length)
            curses.panel.update_panels(); stdscr.refresh()
            
            sleep(self.cluispd)
    
    def set_freq(self, v):
        self.freq = float(v)
        for l in self.loops:
            l.seconds = self.freq

    def set_rr(self, v):
        rr = int(v)
        self.rr = rr
        for l in self.loops:
            l._target.regen(rr)

    def start_latency(self):
        self.latency = True
        for loop in self.loops:
            loop._target.startLatency()

    def stop_latency(self):
        self.latency = False
        for loop in self.loops:
            loop._target.stopLatency()

    def mainloop(self):
        curses.wrapper(self.app)

    def asyncThread(self):
        loop()

    def clean(self):
        try:
            close_all()
        finally:
            if self.sock:
                self.sock.close()
            if self.tcpinput:
                self.tcpinput.delete()
            if self.service:
                self.service.logout()