import Tkinter as tk
import ttk
from ScrolledText import ScrolledText
import os

class App(tk.Frame):
    settings = {}
    output_count = 0
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background='lightgrey')   
         
        self.parent = parent
        parent.protocol("WM_DELETE_WINDOW", self.exit)
        self.initUI()
        
    def initUI(self):
      
        self.parent.title("ChangeMe")
        self.pack(side="top", fill="both", expand=1)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(6, pad=7)
        self.rowconfigure(7, pad=7)

        self.str_tasks = tk.StringVar()
        self.str_tasks.set("Active Tasks: 0")
        self.lbl_tasks = ttk.Label(self, textvariable=self.str_tasks)
        self.lbl_tasks.grid(sticky='w', pady=4, padx=5)
        
        #self.text = ScrolledText(self, state='disabled')
        #self.text.grid(row=1, column=0, columnspan=2, rowspan=6, 
        #    padx=5, sticky=tk.E+tk.W+tk.S+tk.N)
        
        start_btn = ttk.Button(self, text="Start", command=self.start_cmd)
        start_btn.grid(row=1, column=3)

        stop_btn = ttk.Button(self, text="Stop", command=self.stop_cmd)
        stop_btn.grid(row=2, column=3)
        
        hbtn = ttk.Button(self, text="Help", command=self.help)
        hbtn.grid(row=7, column=0, padx=5)

        qbtn = ttk.Button(self, text="Quit", command=self.exit)
        qbtn.grid(row=7, column=3)


        login_btn = ttk.Button(self, text="Create Input", command=self.login)
        login_btn.grid(row=3, column=3, sticky='n')

        ttk.Label(self, text="freq").grid(row=0,column=4, sticky='s')
        freq_scale = tk.Scale(self, from_=2, to=0.10, 
                                resolution=0.01, 
                                orient='vertical', 
                                length=200,
                                command=self.set_freq)
        freq_scale.set(self.freq)
        freq_scale.grid(row=1, column=4, sticky='n', rowspan=3, padx=10)

        ttk.Label(self, text="response\nchance").grid(row=4,column=4, rowspan=1,sticky='s')
        rr_scale = tk.Scale(self, from_=100, to=0, 
                                resolution=1, 
                                orient='vertical', 
                                length=200,
                                command=self.set_rr)
        rr_scale.set(50)
        rr_scale.grid(row=5, column=4, sticky='n', rowspan=3, padx=10)   

    def output(self, text, newline=True):
        print text
        #self.output_count += 1
        #self.text.config(state='normal')
        #if self.output_count == 100:
            #print h.heap()
        #    self.output_count -= 9
        #    self.text.delete('0.0','10.0')
        #self.text.insert('end', newline and text+"\n" or text)
        #self.text.see('end')
        #self.text.config(state='disabled') 

    def start_cmd(self):
    	self.output('starting')
    def stop_cmd(self):
    	self.output('stopping')
    def help(self):
    	self.output('not very helpful')
    def exit(self):
        self.quit()

class Dialog(tk.Toplevel):

    def __init__(self, parent, title = None, **kwargs):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.kwargs = kwargs

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default='active')
        w.pack(side='left', padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side='left', padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override

def main():
  
    root = tk.Tk()
    root.geometry("960x600")
    app = App(root)
    root.mainloop()  


if __name__ == '__main__':
    main()