import multiprocessing
import multiprocessing.pool

class NoDaemonProcess(multiprocessing.Process):
    # робимо щоб запит на daemon атрибут завжди повертав False
    @property
    def daemon(self):
        return False
    
    @daemon.setter
    def daemon(self, value):
        pass
    #daemon = property(_get_daemon, _set_daemon)

class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess

class MyPool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs['context'] = NoDaemonContext()
        super(MyPool, self).__init__(*args, **kwargs)
