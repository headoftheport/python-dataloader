from . import Base

class Bar(Base):
    suffix = '%(index)d/%(max)d [%(percent)d%%] [%(elapsed_td)s]'
    start = " |"
    end = "| "
    def __init__(self, message, max, *args, **kwargs):
        super(Bar, self).__init__(*args, **kwargs)
        self.message = message
        self.max = max

    def update(self):
        fill_length = int(self.width*self.progress)
        empty_length = self.width - fill_length
        bar =  self.fill * fill_length
        empty  = self.empty * empty_length
        suffix = self.suffix % self
        line = ''.join([self.message, self.start, bar, empty, self.end, suffix])
        self.write(line)

