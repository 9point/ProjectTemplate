import time
import threading

class Val:
    def __init__(self):
        self._val = None

    def get_val(self):
        return self._val

    def set_val(self, val):
        self._val = val

 
def generator(val):
    while True:
        yield val.get_val()
        print('hello')
        time.sleep(2)

def loop(generator):
    for val in generator:
        print(val) 


def run_generator(val):
    thread = threading.Thread(target=loop, args=(generator(val),))
    thread.start()


print('generating')
val = Val()
val.set_val(5)

run_generator(val)
print('done generating')

time.sleep(5)
print('updating val to 10')
val.set_val(10)


