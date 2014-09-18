#!/usr/bin/env python
import sys, re, datetime, time, socket, threading, signal
from getpass import getpass

from lib.eventgenlib import create_splunk_input, connect_to_splunk
from config import CONFIG

import splunklib.client as client

user = None
password = None
count = 0
threads = []

current_milli_time = lambda: int(round(time.time() * 1000))

def login(user, password, config):
    print 'connecting to', config['host']+':'+str(config['splunk_rest_port'])
    try:
        service = connect_to_splunk(config, user, password)
    except client.AuthenticationError:
        print "login failed"
        sys.exit()
    sock, tcpinput = create_splunk_input(service, config)
    return service, sock, tcpinput

def getFileInfo():
	with open(sys.argv[1]) as f:
		data = f.readlines()
		rows += len(data)
		if not first:
			first = data[0].split('+',1)[0]
		last = data[-1].split('+',1)[-0]
	dt = datetime.datetime.fromtimestamp
	first = dt(float(first)/1000)
	last = dt(float(last)/1000)
	print last-first, 'length'
	print rows, 'rows'

def genLines(sock):
    global count
    with open(sys.argv[1]) as f:
        while True:
            for line in f:
                count+=1
                if not count%10:
                    print count,'events sent'
                now = current_milli_time()

                line = str(now)+line[13:]
                #print line
                sock.send(line+'\n\n\n')
                time.sleep(0.5)
            f.seek(0)

def createGenerators(ka):
    threads = []
    for c in CONFIG['linegen'].keys():
        print(' '.join(['starting:', c]))
        t = CONFIG['linegen'][c]['callback'](
                    ka=ka,
                    name=c,
                    config=CONFIG['linegen'][c]
                    )
        t.daemon = True
        threads.append(t)
    return threads

def signal_handler(signal, frame):
        global threads
        print('closing threads...')
        [t.stop() for t in threads]
        [t.join() for t in threads]
        sys.exit()

class KeepAlive(object):
    sock = None
    service = None
    tcpinput = None
    regen = False
    def __init__(self, user, password, config):
        self.user = user
        self.password = password
        self.config = config
        self.lock = threading.Lock()
        self.createSocket()

    def createSocket(self):
        self.regen = True
        while True:
            try:
                self.service, self.sock, self.tcpinput = login(self.user, self.password, self.config)
                self.regen = False
                break
            except socket.error, e:
                print e
                time.sleep(5)

    def getSocket(self):
        if self.regen:
            print 'socket requested, but none to give'
            return None
        else:
            print 'gave new socket'
            return self.sock

    def regenSocket(self):
        with self.lock:
            if not self.regen:
                self.regen = True
                print 'regenerating socket'
                self.createSocket()

    def clean(self):
        print 'cleaning...'
        if self.sock:
            self.sock.close()
        if self.tcpinput:
            self.tcpinput.delete()
        if self.service:
            self.service.logout()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    global user, password
    if not user:
        user = raw_input('Username: ')
    if not password:
        password = getpass()

    ka = KeepAlive(user, password, CONFIG)
    try:
        print 'connected!'
        global threads
        threads = createGenerators(ka)
        print 'starting', len(threads), 'threads...'
        [t.start() for t in threads]
        signal.pause()

    finally:
        ka.clean()
        sys.exit()

if __name__ == "__main__":
	main()