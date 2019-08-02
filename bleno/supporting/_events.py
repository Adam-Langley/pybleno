from ._jshelpers import DotDict
from ._require import require

sys = require(__file__, 'sys')
module = sys.modules[__name__]

debug = require(__file__, '_debug')('events')

class EventEmitter(DotDict):
    def __init__(self):
        self._listeners = {}

    def on(self, name, handler=None):
        # print('1.')
        # print(self)
        # print('2.')
        # print(name)
        if not name in self._listeners:
            self._listeners[name] = []
        scope = self._listeners[name]
        scope.append(handler)
        self.emit('newListener', name)

    def removeListener(self, name, handler):
        if name in self._listeners:
            scope = self._listeners[name]
            scope.remove(handler) 
    
    def emit(self, name, *args):
        scope = self._listeners[name] if name in self._listeners else None
        if scope:
            for listener in scope:
                listener(*args)

    def once(self, event, handler):
        def temporary_handler(event, *arguments):
            self.removeListener(event, temporary_handler)
            handler(*arguments)

        self.on(event, temporary_handler)                

module.exports = EventEmitter

EventEmitter.EventEmitter = EventEmitter
