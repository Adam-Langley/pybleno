from .hci_socket import Emit
from . import UuidUtil


class Characteristic(dict):
    RESULT_SUCCESS = 0x00
    RESULT_INVALID_OFFSET = 0x07
    RESULT_ATTR_NOT_LONG = 0x0b
    RESULT_INVALID_ATTRIBUTE_LENGTH = 0x0d
    RESULT_UNLIKELY_ERROR = 0x0e

    def __init__(self, options=None):
        super().__init__()
        if options is None:
            options = {}
        self['uuid'] = UuidUtil.removeDashes(options['uuid'])
        self['properties'] = options['properties'] if 'properties' in options else []
        self['secure'] = options['secure'] if 'secure' in options else []
        self['value'] = options['value'] if 'value' in options else None
        self['descriptors'] = options['descriptors'] if 'descriptors' in options else []

        self.maxValueSize = None
        self.updateValueCallback = None

        if self['value'] and (len(self['properties']) != 1 or self['properties'][0] != 'read'):
            raise Exception('Characteristics with value can be read only!')

        if 'onReadRequest' in options:
            self.onReadRequest = options['onReadRequest']

        if 'onWriteRequest' in options:
            self.onWriteRequest = options['onWriteRequest']

        if 'onSubscribe' in options:
            self.onSubscribe = options['onSubscribe']

        if 'onUnsubscribe' in options:
            self.onUnsubscribe = options['onUnsubscribe']

        if 'onNotify' in options:
            self.onNotify = options['onNotify']

        if 'onIndicate' in options:
            self.onIndicate = options['onIndicate']

        self.on('readRequest', self.onReadRequest)
        self.on('writeRequest', self.onWriteRequest)
        self.on('subscribe', self.onSubscribe)
        self.on('unsubscribe', self.onUnsubscribe)
        self.on('notify', self.onNotify)
        self.on('indicate', self.onIndicate)

    def onReadRequest(self, offset, callback):
        callback(self.RESULT_UNLIKELY_ERROR, None)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        callback(self.RESULT_UNLIKELY_ERROR)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        self.maxValueSize = maxValueSize
        self.updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        self.maxValueSize = None
        self.updateValueCallback = None

    def onNotify(self):
        pass

    def onIndicate(self):
        pass

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__dict__.__cmp__(dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __unicode__(self):
        return unicode(repr(self.__dict__))


Emit.Patch(Characteristic)
