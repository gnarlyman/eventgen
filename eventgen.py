import sys
from Tkinter import Tk

from config import CONFIG

from app import EventGenApp
from clui import EventGenCLI

from lib.eventgenlib import create_splunk_input, connect_to_splunk

__version__ = "0.1.5"
__author__ = "Mike Schon"

'''
EventGen

Changelog
0.0.1
-Basic asynchronous event loop for event generation
-TEST_CASE_1 added

0.0.2 
-Fixed high cpu usage, added a very brief sleep to the event loop

0.0.3
-Moved some things to config.py
-Now using Splunk tcp input, rather than http-stream, its just faster

0.0.4
-added rest port as a config option
-modulaized everything
-TEST_CASE_2 added

0.0.5
-added tkinter gui
-all current functionality integrated into gui

0.0.6
-added new gui functionality, can control certain 
    aspects of event generation
-a truely ugly gui, as ugly as it gets

0.0.7
-minor fixes

0.0.8
-added test_case_3, FW req resp messages

0.0.9
-merged test_case_1 and test_case_3, they are related
-merged test_case_2 with a new test case, they are related
-code cleanup

0.1.0
-rewrote the test_case module, much better

0.1.1
-log window clears itself occasionally, its crude but about the only way
-added optional cli support, no configuration possible while running

0.1.2
-modularized everything, again, but really this time
-FIXME! - memory leak in tkinter text module on mac osx
-new text ui, some functionality now possible via cli

0.1.3
-Added assetID randomization to logs

0.1.4
-Workaround for tkinter memory leak, print to console for now
-functionized backlisting
-CLUI now the default, though blacklisting is still not implemented
-more CLUI options
-CONFIG is much more configurable

0.1.5
-Added Canoe logs, test_case_3 and 4

0.1.6
-Added LineGen
'''

def main():
    # GUI
    if '-g' in sys.argv:
        root = Tk()
        root.geometry("540x600")
        app = EventGenApp(root, CONFIG, __version__)
        root.mainloop()

    # CLUI
    else:
        try:
            ev = EventGenCLI(CONFIG, __version__)
            ev.login()
            ev.startCases()
            ev.start()
            ev.mainloop()
        except KeyboardInterrupt:
            print '\nquitting...'
        except:
            raise
        finally:
            print 'cleaning...'
            ev.clean()

if __name__ == '__main__':
    print "EventGen %s" % __version__
    main()
