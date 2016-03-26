from Queue import Queue, Empty


class IterableQueue(Queue):
    pastitems = []

    def __iter__(self):
        return self

    def set_to_iterator(self, set_, iter_):
        assert isinstance(set_, bool)
        if set_:
            while not self.empty():
                self.get_nowait()

        for x in iter_:
            self.put_nowait(x)

        return self

    def __len__(self):

        if self.empty():
            return 0
        else:

            i = 0

            putback = []

            while not self.empty():
                x = self.get_nowait()
                putback.append(x)
                i += 1

            for x in putback:
                self.put_nowait(x)

            return i

    def next(self):
        try:
            x = self.get_nowait()
        except Empty:
            return None
        self.pastitems.append(x)
        try:
            self.put(self.get())
        except Empty:
            self.close()
        return x

    def close(self, ):
        for x in self.pastitems:
            self.put(x)
