import code
import multiprocessing.connection
import sys,os,time
from time import sleep
import fcntl
import threading

port = int(sys.argv[1])
conn = multiprocessing.connection.Client(('localhost', port), authkey=b"secret")
obj = None


print('Session initialized.')


class MyConsole (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.c = code.InteractiveConsole()

    def run(self):
        global obj
        while True:
            obj = conn.recv()
            temp = str(obj)
            temp = temp.rstrip('\r\n')
            temp = temp.replace('\t', '    ')
            if 'NEWLINE' in temp:
                temp = ""
            #print(":" + obj)
            self.c.push("" + temp)
            time.sleep(1/4)
        #self.c.push("from time import sleep")
        #self.c.push("print('hello')")
        #self.c.push("print('hell')")
        #self.c.push("print('hell')")
        #self.c.push("while True:")
        #self.c.push(" print('wat')")
        #self.c.push(" print('wasdfdsfat')")
        #self.c.push(" sleep(2)")
        #self.c.push("")
        #self.c.push("print('hell')")


thread = MyConsole()
thread.start()

while True:

    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(1)
