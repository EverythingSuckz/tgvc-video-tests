

class Queue:
    def __init__(self):
        self.queue = dict()
    def add(self, chat: int, data: dict):
        queue = self.queue.get(chat, None)
        if not queue:
            self.queue[chat] = []
        self.queue[chat].append(data)
        return len(self.queue) + 1
    def get(self, chat, pop=True):
        queue = self.queue.get(chat, None)
        if not queue:
            self.queue[chat] = []
        if pop:
            try:
                next = self.queue[chat].pop(0)
            except IndexError:
                next = None
            return next
        return self.queue[chat]