import random, time, threading, socket, logging

from lib.eventgenlib import now, clear_blacklist, clear_latency, current_milli_time
from lib.async import CallLater

class LineGen(threading.Thread):
    sock = None
    logger = logging.getLogger('linegen')
    def __init__(self, *args, **kwargs):
        super(LineGen, self).__init__()
        self.config = kwargs['config']
        self.name = kwargs['name']
        self._stop = threading.Event()
    
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self): 

        self.logger.debug(' '.join(['LineGen:', self.config['file']]))
        try:
            self.config['function'](self)
        except Exception, err:
            self.logger.exception(err, exc_info=True)
            raise

class Case(object):
    iterations = 0
    sinfo = None
    output = None
    sock = None
    name = None
    cut_items = []
    active_blacklist = False
    active_latency = False
    settings = None
    rr = 50
    RR_RAND = []

    def __init__(self, loop, *args, **kwargs):
        self.loop = loop
        self.name = kwargs['name']
        self.sinfo = kwargs['config']
        self.output = kwargs['output']
        self.sock = kwargs['sock']
        self.commands = kwargs['commands'].copy()

    def regen(self, rr):
        self.RR_RAND = []
        for _ in xrange(rr):
            self.RR_RAND.append(False)
        for _ in xrange(1):
            self.RR_RAND.append(True)
        random.shuffle(self.RR_RAND)

    def startLatency(self):
        self.active_latency = True
        self.output(' '.join([self.name+':', "generating high latency"]))

    def stopLatency(self):
        self.active_latency = False
        self.output('clearing latency')

    def blacklist(self, bl):
        self.active_blacklist = True
        identities = bl
        self.output('blacklisting:\n%s' % '\n'.join(identities))
        for d in list(self.sinfo['values']):
            if d['identity'] in identities:
                self.cut_items.append(self.sinfo['values'].pop(self.sinfo['values'].index(d)))

    def clear_blacklist(self):
        self.active_blacklist = False
        self.output('clearing blacklist')
        self.sinfo['values'].extend(self.cut_items)
        del self.cut_items[:]

    def _exec(self):
        self.iterations += 1

        # Randomly choose a combination of values from the json input
        choice = random.choice(self.sinfo['values'])

        # Add additional random values
        for name, func in self.sinfo['functions'].items():
            arg = None
            if isinstance(func, list):
                fn = func[0]
                arg = func[1]
                if arg:
                    choice.update({name:fn(arg)})
                else:
                    choice.update({name:fn()})
            else:
                choice.update({name:func()})

        # Prepare timestamp for iteration
        timestamp = now()
        # tracks how many milliseconds offset of timestamp
        offset = 0

        high_latecy = False
        missing_log = False
        # iterate over each log in the log file template
        for i in xrange(len(self.sinfo['data'])):
            # iteration activities, don't execute on first iteration
            if not i==0:
                if random.choice(self.RR_RAND):
                    missing_log = True
                    break
                offset += self.active_latency and random.randint(2200,5000) or random.randint(1,50)
                if offset > 1000: high_latecy = True

            # Add timestamp to log
            choice.update({'timestamp':timestamp+offset})
            # Send the log to splunk
            self.sock.send(self.sinfo['data'][i]%choice+'\n\n\n')

        # status messages, shows the low probability events (if any)
        self.output(' '.join(['%-18s' %self.name+':', '%d' % self.iterations, choice['identity'], 'duration(ms):', '%d' % offset, (  
            high_latecy and "- High Latency" 
            or missing_log and "- No Response" 
            or ""
            )])
        )

