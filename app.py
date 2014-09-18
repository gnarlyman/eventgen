import Tkinter as tk
import ttk
import threading

from collections import OrderedDict
from getpass import getpass

from lib.async import CallEvery, CallLater, loop, close_all, _tasks
from lib.gui import App, Dialog

from lib.eventgenlib import create_splunk_input, connect_to_splunk

import splunklib.client as client

class LoginDialog(Dialog):

    def body(self, master):
        self.title("Splunk Login")

        ttk.Label(master, text="Username:").grid(row=0)
        ttk.Label(master, text="Password:").grid(row=1)

        self.e1 = ttk.Entry(master)
        self.e2 = ttk.Entry(master, show="*")

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1 # initial focus

    def apply(self):
        u = self.e1.get() or None
        p = self.e2.get() or None
        self.result = [u,p]

    def getResult(self):
        return self.result

class BlacklistDialog(Dialog):

    def body(self, master):
        self.title("Blacklist mADMs")

        text = ("Use scroll wheel to see all mADMs\n"
                "click a many as you want to blacklist")
        ttk.Label(self, text=text).pack(side='top')

        self.madm_box = tk.Listbox(self, selectmode='multiple', height=20)
        self.madm_box.pack()
        for name in self.kwargs['identities']:
            self.madm_box.insert('end', name)
        #self.case_box.bind("<Double-Button-1>", self.run_test)

    def apply(self):
        self.result = [self.kwargs['identities'][int(item)] for item in self.madm_box.curselection()]

    def getResult(self):
        return self.result

class EventGenApp(App):
    service = None
    sock = None
    tcpinput = None
    loops = []
    freq = 1
    config = None
    commands = OrderedDict([
        ('start latency', False), 
        ('stop latency', False),
        ('blacklist', False),
        ('clear blacklist', False),
    ])

    def __init__(self, parent, CONFIG, v):
        App.__init__(self, parent)
        self.config = CONFIG
        self.t = threading.Thread(target=self.asyncThread)
        parent.title('EventGen %s' % v)

        self.case_box = tk.Listbox(self)
        self.case_box.grid(row=4, column=3, sticky='n')
        for name in self.config['cases'].keys():
            self.case_box.insert('end', name)
        self.case_box.bind("<Double-Button-1>", self.run_test)
        ttk.Label(self, text="test cases").grid(row=4,column=3, sticky='s', pady=1)

        self.cmd_box = tk.Listbox(self)
        self.cmd_box.grid(row=5, column=3, sticky='n', pady=20)
        for name in self.commands.keys():
            self.cmd_box.insert('end', name)
        self.cmd_box.bind("<Double-Button-1>", self.run_cmd)
        ttk.Label(self, text="commands").grid(row=5,column=3, sticky='s', pady=21)

        #start_btn = ttk.Button(self, text="Debug", command=self.debug)
        #start_btn.grid(row=7, column=4)

    def debug(self):
        pass

    def set_freq(self, v):
        self.freq = float(v)
        for l in self.loops:
            l.seconds = self.freq

    def set_rr(self, v):
        rr = int(v)
        self.rr = rr
        for l in self.loops:
            l._target.regen(rr)

    def start_cmd(self):
        if self.service is None:
            pass
        if self.sock is None:
            self.output('no socket, create an input')
            return
        if not len(self.loops):
            self.output('no tasks, add some')
            return
        self.output('starting')
        self.t = threading.Thread(target=self.asyncThread)
        self.t.start()

    def login(self):
        d = LoginDialog(self.parent)
        result = d.getResult()
        if result:
            user, pswd = result
            if not user or not pswd:
                self.login()
            try:                
                self.output(' '.join(['connecting to', self.config['host']+':'+str(self.config['splunk_rest_port'])]))
                self.service = connect_to_splunk(self.config, user, pswd)
                #self.output(str(self.service))
                self.sock, self.tcpinput = create_splunk_input(self.service, self.config)
                self.output('input created successfully')
            except client.AuthenticationError:
                self.output('login failed')
        else:
            self.output('cancelled')

    def run_test(self, ev):
        if self.sock is None:
            self.output('no socket, create an input')
            return
        clicked = self.config['cases'].keys()[ev.widget.nearest(ev.y)]
        #for l in self.loops:
        #    if l.name ==clicked:
        #        self.output('task already added, choose another')
        #        return
        loop = CallEvery(self.freq,
                    self.config['cases'][clicked]['callback'],
                    sock=self.sock,
                    name=clicked,
                    output=self.output,
                    config=self.config['cases'][clicked],
                    commands=self.commands,
                    )
        loop._target.regen(self.rr)
        self.loops.append(loop)
        self.output('added %s' % clicked)
        self.output('%d tasks queued' % (len(_tasks)))
        self.str_tasks.set("Active Tasks: %d" % len(_tasks))

    def run_cmd(self, ev):
        if not len(self.loops):
            self.output('no tasks, add some')
            return
        if not self.t.isAlive():
            self.output('not running, click Start')
            return
        clicked = self.commands.keys()[ev.widget.nearest(ev.y)]
        if clicked == 'blacklist':
            # Enable blacklist for selected mADMs or All
            identities = []
            for loop in self.loops:
                if loop._target.active_blacklist:
                    self.output('already blacklisting, clear the blacklist first')
                    return
                identities.extend([str(d['identity']) for d in loop._target.sinfo['values']])
            identities = sorted(list(set(identities))) # dedup
            d = BlacklistDialog(self.parent, identities=identities)
            result = d.getResult()
            if not result:
                self.output('cancelled')
                return
            for loop in self.loops:
                loop._target.blacklist(result)

        elif clicked == 'clear blacklist':
            for loop in self.loops:
                loop._target.clear_blacklist()

        elif clicked == 'start latency':
            for loop in self.loops:
                loop._target.startLatency()

        elif clicked == 'stop latency':
            for loop in self.loops:
                loop._target.stopLatency()

    def asyncThread(self):
        loop()
        #self.output('all tasks done')


    def stop_cmd(self):
        self.output('stopping')
        del self.loops[:]
        close_all()
        #print _tasks
        self.str_tasks.set("Active Tasks: %d" % len(_tasks))

    def help(self):
        self.output('\n'.join([
            '-'*80,
            'EventGen %s - Help' % __version__,
            'start by clicking \'Create Input\', then login to Splunk',
            'add test cases by double-clicking them',
            'then click \'Start\' to start generating events',
            'once started, run commands by double-clicking them',
            'you can stop the generator by clicking stop, this also clears all tasks',
            'Note: config.py must be configured with your splunk instance info',
            '-'*80,
            ]))

    def exit(self):
        print 'quitting'
        close_all()
        if self.sock:
            self.sock.close()
        if self.tcpinput:
            self.tcpinput.delete()
        if self.service:
            self.service.logout()
        self.quit()