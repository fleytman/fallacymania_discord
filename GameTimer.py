# based on comment S.G. Harmonia on https://stackoverflow.com/posts/26090325/revisions

import time
from threading import Timer


class RenewableTimer():
    def __init__(self, timeout, callback):
        self.start_time = time.time()
        self.timeout = timeout
        self.callback = callback
        self.timer = Timer(timeout, callback)

    def cancel(self):
        self.timer.cancel()
        self.timer.join()

    def start(self):
        self.start_time = time.time()
        self.timer.start()

    def pause(self):
        self.cancel_time = time.time()
        self.timer.cancel()
        self.timer.join()
        return self.get_actual_time()

    def resume(self):
        self.timeout = self.get_actual_time()
        self.timer = Timer(self.timeout, self.callback)
        self.timer.start()

    def get_actual_time (self):
        return self.timeout - (self.cancel_time - self.start_time)
