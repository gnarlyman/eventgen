#!/usr/bin/env python
import sys, re, datetime, time, socket
from getpass import getpass

from lib.eventgenlib import create_splunk_input, connect_to_splunk
from config import CONFIG

import splunklib.client as client

user = None
password = None
count = 0

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

def clean(sock, tcpinput, service):
    print 'cleaning...'
    if sock:
        sock.close()
    if tcpinput:
        tcpinput.delete()
    if service:
        service.logout()

def main():
    global user, password
    if not user:
        user = raw_input('Username: ')
    if not password:
        password = getpass()

    try:
        service, sock, tcpinput = login(user, password, CONFIG)
        print 'connected!'
        genLines(sock)
    except socket.error, e:
        print e
        print 'reconnecting in 5 seconds...'
        time.sleep(5)
        main()
    except:
        clean(sock, tcpinput, service)
        sys.exit()

if __name__ == "__main__":
	main()