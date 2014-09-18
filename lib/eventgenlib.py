import time
import random
import socket

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