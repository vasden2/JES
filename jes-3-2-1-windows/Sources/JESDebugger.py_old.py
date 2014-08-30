import sys
import cmd
import bdb
import pdb
import threading
import time
import JESDBVariableWatcher


line_prefix = '\n-> '
prompt = '(jesdb) '

class JESDebugger(pdb.Pdb):
    
    def __init__(self, interpreter):
        pdb.Pdb.__init__(self)
        self.text_mode = 0  # command line interface if on
        self.step_mode = 0  # step mode is when we let the user press the step button
        self.running = 0    # running is when we are inside a debugger run, i.e. we
                            # we're debugging a command(not waiting for a new command)
        self.lock = threading.Lock()    # we need a lock for the wait mechanism
        self.cond = threading.Condition(self.lock)
        self.interpreter = interpreter
        self.speed = 5      # cycles per second

        self.watcher = JESDBVariableWatcher.JESDBVariableWatcher(self)  # not necessarily have to be showing
    
        self.cmd = None
        self.reset()

    def setSpeed(self, speed):
        self.speed = speed

    def addVariable(self, var):
        self.watcher.addVariable(var)
        
    # Override Bdb methods (except user_call, for now)
    def user_line(self, frame):
        """This function is called when we stop or break at this line."""
        #print 'in user_line---'
        if frame.f_code.co_filename == self.interpreter.program.filename or not self.running:
            #if self.break_here(frame) or not self.running:
            self.running = 1
            self.interaction(frame, None)
        

    def user_return(self, frame, return_value):
        pass
        #"""This function is called when a return trap is set here."""
        #print 'in user_return'
        #frame.f_locals['__return__'] = return_value
        #print '--Return--'
        #if self.break_here(frame):
        #    self.interaction(frame, None)

    def user_exception(self, frame, (exc_type, exc_value, exc_traceback)):
        if self.break_here(frame):
            self.interaction(frame, None)
        #"""This function is called if an exception occurs,
        #but only if we are to stop at or just below this level."""
        #frame.f_locals['__exception__'] = exc_type, exc_value
        #if type(exc_type) == type(''):
        #    exc_type_name = exc_type
        #else: exc_type_name = exc_type.__name__
        #print exc_type_name + ':', _saferepr(exc_value)
        #self.interaction(frame, exc_traceback)

        
    # this is the main interface from the outside
    def runCommand(self, cmd):
        # the debugger is running already, that means there
        # is already a jesThread sleeping waiting for a signal.
        # let's give it the signal
        self.cmd = cmd
        self.lock.acquire()
        self.cond.notifyAll()
        self.lock.release()
        

        
    def print_frame(self, frame):
        self.print_stack_entry((frame, frame.f_lineno))

        
    # General interaction function    
    def interaction(self, frame, traceback):
        
        if self.text_mode:
            cmd = ''
            stop = 0
            self.print_frame(frame)
            while not stop:
                self.setup(frame, traceback)
                self.interpreter.jesThread.threadCleanup()
                self.lock.acquire()
                self.cond.wait()     # wait for the program to signal
                self.lock.release()
                self.interpreter.jesThread.initialize()
                stop = self.onecmd(self.cmd)
                
        else:
            # if we're not in stop mode then we're in...
            # unique to JESDB...the running debug mode!!
            # get line and frame number
            import linecache, time
            self.setup(frame, traceback)
            lineno = frame.f_lineno
            filename = self.interpreter.program.filename
            line = linecache.getline(filename, lineno)
            self.watcher.snapShot(lineno, line)
            # we assume speed is non-zero at this point
            time.sleep(1/self.speed)
    
    def run(self, cmd, globals=None, locals=None):
        self.running = 0
        self.watcher.clear()
        if len(self.watcher.getVariables()) > 0 and not self.watcher.visible:
            self.watcher.setVisible(1)
        pdb.Pdb.run(self, cmd, globals, locals)
        self.running = 0
        
        
    def runeval(self, cmd, globals=None, locals=None):
        self.running = 0
        pdb.Pdb.runeval(self, cmd, globals, locals)
        self.running = 0
