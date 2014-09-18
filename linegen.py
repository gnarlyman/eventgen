#!/usr/bin/env python
import sys, re, datetime, time, socket, threading, signal
from getpass import getpass

from lib.eventgenlib import create_splunk_input, connect_to_splunk
from config import CONFIG

import splunklib.client as client

threads = []

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

def createGenerators():
    threads = []
    for c in CONFIG['linegen'].keys():
        if CONFIG['linegen'][c]['disabled']:
            continue
        print(' '.join(['starting:', c]))
        t = CONFIG['linegen'][c]['callback'](
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

def main():
    signal.signal(signal.SIGINT, signal_handler)
    try:
        print 'connected!'
        global threads
        threads = createGenerators()
        print 'starting', len(threads), 'threads...'
        [t.start() for t in threads]
        signal.pause()

    finally:
        sys.exit()

if __name__ == "__main__":
	main()