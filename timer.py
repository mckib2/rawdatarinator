from time import time

class Timer():
    
    def __init__(self):
        self.starts = []

    def tic(self,name=None):
        # Create a named time
        self.starts.append((name,time()))
        
    def toc(self):
        # Grab the last named time off the stack
        t = self.starts.pop()
        
        if t[0] is not None:
            print('%s: %s seconds' % (t[0], (time() - t[1])))
        else:
            print('%s seconds elapsed' % (time() - t[1]))

