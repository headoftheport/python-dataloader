from . import Base

class Timer(Base):
    suffix = '[%(elapsed_td)s]'
    padding = ' : '
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)

    def update(self):
        suffix = self.suffix % self
        line = ''.join([self.message, self.padding, suffix])
        self.write(line)