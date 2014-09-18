import curses
import curses.ascii

from curses.textpad import Textbox

class CustomTextbox(Textbox):
    """
    Overridden since the original intent of Textbox was
    to mimic emacs, and no support was added for the enter key.
    Added this support by putting 2 lines of code into this function. 
    Whala.
    """

    def do_command(self, ch):
        "Process a single editing command."
        (y, x) = self.win.getyx()
        self.lastcmd = ch
        if curses.ascii.isprint(ch):
            if y < self.maxy or x < self.maxx:
                self._insert_printable_char(ch)
        elif ch == 10: # and now we magically know when 'enter' is pressed
        	return 0 
        elif ch == curses.ascii.SOH:                           # ^a
            self.win.move(y, 0)
        elif ch in (curses.ascii.STX,curses.KEY_LEFT, curses.ascii.BS,curses.KEY_BACKSPACE):
            if x > 0:
                self.win.move(y, x-1)
            elif y == 0:
                pass
            elif self.stripspaces:
                self.win.move(y-1, self._end_of_line(y-1))
            else:
                self.win.move(y-1, self.maxx)
            if ch in (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
        elif ch == curses.ascii.EOT:                           # ^d
            self.win.delch()
        elif ch == curses.ascii.ENQ:                           # ^e
            if self.stripspaces:
                self.win.move(y, self._end_of_line(y))
            else:
                self.win.move(y, self.maxx)
        elif ch in (curses.ascii.ACK, curses.KEY_RIGHT):       # ^f
            if x < self.maxx:
                self.win.move(y, x+1)
            elif y == self.maxy:
                pass
            else:
                self.win.move(y+1, 0)
        elif ch == curses.ascii.BEL:                           # ^g
            return 0
        elif ch == curses.ascii.NL:                            # ^j
            if self.maxy == 0:
                return 0
            elif y < self.maxy:
                self.win.move(y+1, 0)
        elif ch == curses.ascii.VT:                            # ^k
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
        elif ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        elif ch in (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            if y < self.maxy:
                self.win.move(y+1, x)
                if x > self._end_of_line(y+1):
                    self.win.move(y+1, self._end_of_line(y+1))
        elif ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
        elif ch in (curses.ascii.DLE, curses.KEY_UP):          # ^p
            if y > 0:
                self.win.move(y-1, x)
                if x > self._end_of_line(y-1):
                    self.win.move(y-1, self._end_of_line(y-1))
        return 1