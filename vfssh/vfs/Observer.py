from collections import defaultdict


class Observer:
    _observers = defaultdict(dict)

    def __init__(self):
        self._observers[self] = {}

    def observe(self, event_name, callback):
        self._observers[self][event_name] = callback

    def decommission(self):
        self._observers.pop(self)


class Event:
    def __init__(self, obj, trigger, data, auto_fire=True):
        self.obj = obj
        self.trigger = trigger
        self.data = data
        if auto_fire:
            self.fire()

    def fire(self):
        if self.obj in Observer._observers.keys() and self.trigger in Observer._observers[self.obj]:
            a = Observer._observers.get(self.obj).get(self.trigger)
            a(self.data)


class Room(Observer):
    def __init__(self):
        super().__init__()
        print("Room is ready")

    def someone_arrived(self, who):
        print(who + " has arrived!")
