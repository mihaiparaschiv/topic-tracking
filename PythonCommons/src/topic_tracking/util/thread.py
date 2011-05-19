from threading import Thread
from Queue import Queue
import logging


# http://code.activestate.com/recipes/577187-python-thread-pool/


class Worker(Thread):
    """Thread executing tasks from a given tasks queue.
    
    A task is defined as a tuple: (func, args, kwargs)
    """
    
    _logger = logging.getLogger('util.thread.Worker')
    
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kwargs = self.tasks.get()
            try:
                func(*args, **kwargs)
            except Exception, e:
                self._logger.error("Worker error: %s" % e)
                self.tasks.task_done()

class WorkerPool:
    """Pool of workers consuming tasks from a queue."""
    
    def __init__(self, num_workers):
        self.tasks = Queue(num_workers)
        for _ in range(num_workers): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()
