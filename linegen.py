#!/usr/bin/env python
import sys, signal
import logging, logging.handlers
from lib.eventgenlib import create_splunk_input, connect_to_splunk
from config import CONFIG

threads = []

LOG_FILENAME = 'linegen.log'
logger = logging.getLogger('linegen')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
            LOG_FILENAME, maxBytes=10**4, backupCount=3)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

def createGenerators():
    threads = []
    for c in CONFIG['linegen'].keys():
        if CONFIG['linegen'][c]['disabled']:
            continue
        logger.debug(' '.join(['starting:', c]))
        t = CONFIG['linegen'][c]['callback'](
                    name=c,
                    config=CONFIG['linegen'][c]
                    )
        t.daemon = True
        threads.append(t)
    return threads

def signal_handler(signal, frame):
        global threads
        print('')
        logger.debug('closing threads...')
        [t.stop() for t in threads]
        [t.join() for t in threads]
        sys.exit()

def main():
    print('running... see linegen.log for activity')
    print('CTRL+C to quit, might take up to 60 seconds')
    signal.signal(signal.SIGINT, signal_handler)
    try:
        global threads
        threads = createGenerators()
        logger.debug(' '.join(['starting', str(len(threads)), 'threads...']))
        [t.start() for t in threads]
        signal.pause()
    except Exception, err:
        logger.exception(err, exc_info=True)
        raise
    finally:
        sys.exit()

if __name__ == "__main__":
	main()