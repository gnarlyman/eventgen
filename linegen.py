#!/usr/bin/env python
import sys, signal

from lib.eventgenlib import create_splunk_input, connect_to_splunk
from config import CONFIG

threads = []

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