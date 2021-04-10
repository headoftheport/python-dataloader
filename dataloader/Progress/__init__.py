import sys
from time import monotonic
from datetime import timedelta

class Base(object):
    width = 50
    fill = "#"
    empty = ' '
    max = 50
    index = 0
    message = "processing"

    def __init__(self,*args,**kwargs):
        self._start_ts = monotonic()
        self.ts = self._start_ts

    @property
    def progress(self):
        if self.max == 0:
            return 0
        return min( 1, self.index/self.max)
    
    @property
    def percent(self):
        return self.progress * 100

    @property
    def elapsed(self):
        return int(monotonic() - self.ts)

    @property
    def elapsed_td(self):
        return timedelta(seconds=self.elapsed)
        
    def start(self):
        self.ts = monotonic()

    def reset(self):
        self.start()

    def show(self, message = 'elapsed time'):
        self.message = message
        self.update()
        self.finish() 

    def finish(self):
        sys.stdout.write("\n")
        sys.stdout.flush()

    def next(self):
        self.index = self.index + 1
        self.update()

    def update(self):
        pass

    def write(self, line):
        sys.stdout.write('\r'+line)
        sys.stdout.flush()

    def __getitem__(self, key):
        if key.startswith('_'):
            return None
        return getattr(self, key, None)
