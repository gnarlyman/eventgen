import time
import random
import socket
import re
import os
import shutil
from datetime import datetime

import splunklib.client as client

def now():
    """ returns milliseconds since epoch """
    return int(time.time()*1000)

def randhex(len):
    """ returns a random character hex string """
    retstr = '%0'+str(len)+'x'
    return retstr % random.randrange(16**int(len))

def clear_blacklist(loop):
    loop.active_blacklist = False
    print loop.name+':', "clearing blacklist"
    loop.sinfo['values'].extend(loop.cut_items)
    del loop.cut_items[:]

def clear_latency(loop):
	loop.active_latency = False
	print loop.name+':', "clearing latency"

def randid():
	""" returns a random hex ID string """
	return '%08x-%04x-%04x-%04x-%012x' % (random.randrange(16**8), 
									random.randrange(16**4), 
									random.randrange(16**4), 
									random.randrange(16**4), 
									random.randrange(16**12))

def read_file(path, lines=False):
    with open(path) as f:
        if lines:
            data = f.readlines()
        else:
            data = f.read()
    return data

def connect_to_splunk(config, user, password, port=8089):
    return client.connect(  host=config['host'], 
                            port=config['splunk_rest_port'], 
                            username=user, 
                            password=password
                        )

def create_splunk_input(service, config):
    """ Create a TCP input on Splunk for events, connect to the input """
    tcpinput = None
    # look for an input already on Splunk
    for i in service.inputs:
        if i.name == config['splunk_tx_port']:
            tcpinput = i
            break
    if tcpinput is None:
        tcpinput = service.inputs.create(
                                config['splunk_tx_port'], 'tcp', 
                                index=config['index'], 
                                sourcetype=config['sourcetype']
                            )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config['host'], int(config['splunk_tx_port'])))

    return sock, tcpinput

def drange(start, stop, step):
    """ works like range, returns a list """
    r = start
    retval = []
    while r < stop:
        retval.append(r)
        r += step
    return retval

current_milli_time = lambda: int(round(time.time() * 1000))

def rollover(path):
    if os.path.isfile(path):
        shutil.move(path, path+'.old')
    return open(path,'w',0)

def genLines_General(self):
    ''' generator for *hopefully* any file

    '''
    self.logger.debug(' '.join([self.name,'started']))
    ts_re = re.compile(self.config['ts_re'])
    ts_format = self.config['ts_format']
    freq = self.config['freq']
    NO_TS_STRIP = self.config.has_key('NO-TS-STRIP')
    with open(self.config['file']) as in_f:
        count = 0
        out_f = rollover(self.config['output'])
        while not self.stopped():
            lg = []
            for line in in_f:
                if self.stopped():
                    return

                m = ts_re.search(line)
                if m:
                    if len(lg):
                        out_f.write(''.join(lg))
                        count+=1
                        if not count%10:
                            self.logger.info(' '.join([self.name,'-',str(count),'events sent']))
                        time.sleep(freq) 

                    ts = m.group(0)
                    ts_len = len(ts)
                    if NO_TS_STRIP:
                        new_ts = datetime.now().strftime(ts_format)
                    else:
                        new_ts = datetime.now().strftime(ts_format)[:-3]
                    line = new_ts+line[ts_len:]

                    lg=[line]
                else:
                    lg.append(line)
            out_f = rollover(self.config['output'])                    
            in_f.seek(0) 


def genLines_BA(self):
    ''' generator for ba.log
        these logs occur constantly
    '''
    self.logger.debug(' '.join([self.name,'started']))
    with open(self.config['file']) as in_f:
        count = 0
        out_f = rollover(self.config['output'])
        while not self.stopped():
            for line in in_f:
                if self.stopped():
                    return
                count+=1
                if not count%10:
                    self.logger.info(' '.join([self.name,'-',str(count),'events sent']))
                now = current_milli_time()

                ts_len = 13
                line = str(now)+line[ts_len:]
                out_f.write(line)

                time.sleep(0.5)
            out_f = rollover(self.config['output'])
            in_f.seek(0)