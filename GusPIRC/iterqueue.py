from Queue import Queue, Empty

class IterableQueue(Queue):

    pastitems = []

    def __iter__(self):
        return self

    def next(self):
        x = self.get()
        self.pastitems.append(x)
        try:
            self.put(self.get())
        except Empty:
            close()
        return x

    def close(self):
        for x in pastitems:
            self.put(x)