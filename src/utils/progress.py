import sys

class Progress:
    percentage:int
    label:str
    def __init__(self, label:str):
        self.label = label
        self.percentage = -1
        self.update(0)
    
    def update(self, percentage:int):
        if self.percentage < percentage:
            self.percentage = percentage
            sys.stdout.write(self.label + "... %s%%\r" % (self.percentage))
            sys.stdout.flush()
    
    def finish(self, message:str = ''):
        self.update(100)
        sys.stdout.write(self.label + "... %s%%" % (self.percentage))
        sys.stdout.flush()
        sys.stdout.write(message + '\n')