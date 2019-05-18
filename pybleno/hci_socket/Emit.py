def on(self, event, handler):
    self._events = self._events
    handlers = self._events[event] = self._events[event] if event in self._events else []
    handlers.append(handler)


def off(self, event, handler):
    handlers = self._events[event] = self._events[event] if event in self._events else []
    handlers.remove(handler)


def emit(self, event, arguments):
    # print self._events
    # print self._events[event]
    handlers = self._events[event] if event in self._events else []
    for handler in handlers:
        handler(*arguments)


def once(self, event, arguments, handler):
    def temporary_handler(*arguments):
        self.off(event, temporary_handler)
        handler(*arguments)

    self.on(event, temporary_handler)


# class Emit:
def Patch(clzz):
    clzz.on = on
    clzz.emit = emit
    clzz.off = off
    clzz.once = once

    old_init = clzz.__init__

    def new_init(self, *k, **kw):
        self._events = {}
        old_init(self, *k, **kw)

    clzz.__init__ = new_init

# Patch = staticmethod(Patch)
