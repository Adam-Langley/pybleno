import sys
import os
import re
from array import array
import json
import struct

from ._require import require

def exports(name):
    module = sys.modules[name]
    module.exports = DotDict()
    return module

def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the
    instance as the first argument, i.e. "self".
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method

def parseFloat(value):
    return float(re.match('([0-9]+(.[0-9]+)?)', value).group(1))
    
def parseInt(value):
    return int(re.match('([0-9]+(.[0-9]+)?)', value).group(1))

def preIncrement(name, local={}):
    #Equivalent to ++name
    if name in local:
        local[name]+=1
        return local[name]
    globals()[name]+=1
    return globals()[name]

def postIncrement(name, local={}):
    #Equivalent to name++
    if name in local:
        print(name + 'is in locals, and value is ' + str(local[name]))
        local[name]+=1
        print(name + 'is in locals DONE, and value is ' + str(local[name]))
        return local[name]-1
    else:
        print(name + ' WAS NOT IN LCOALS!')
    globals()[name]+=1
    return globals()[name]-1    
    
def preDecrement(name, local={}):
    #Equivalent to --name
    if name in local:
        local[name]-=1
        return local[name]
    globals()[name]-=1
    return globals()[name]

def postDecrement(name, local={}):
    #Equivalent to name--
    if name in local:
        local[name]-=1
        return local[name]+1
    globals()[name]-=1
    return globals()[name]+1    
# def bind(to, handler):
#     return handler

# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
            
class process:
    class env:
        BLENO_DEVICE_NAME = "raspberrypi"
        BLENO_HCI_DEVICE_ID = "0"
        BLENO_ADVERTISING_INTERVAL = "1000"
        HCI_CHANNEL_USER = None

    def on(name, handler):
        pass

@staticmethod
def _hostname():
    return 'raspberrypi'

bind(os, _hostname, 'hostname')

class OctetString(array):
    def __new__(cls, buffer):
        return array.__new__(cls, 'B', buffer)

    def __getitem__(self, row):
        return array.__getitem__(self, row) if isinstance(row, slice) or row < len(self) else None

def buffer(arg):
    def readUInt8(self, offset):
        return self[offset]

    def readUInt16LE(self, offset):
        return struct.unpack("<H", self[offset:offset+2])[0]

    def readUInt16BE(self, offset):
        return struct.unpack(">H", self[offset:offset+2])[0]

    def writeUInt8(self, value, offset):
        struct.pack_into("<B", self, offset, value)

    def writeUInt16BE(self, value, offset):
        struct.pack_into(">H", self, offset, value)

    def writeUInt16LE(self, value, offset):
        struct.pack_into("<H", self, offset, value)

    def writeUInt32LE(self, value, offset):
        struct.pack_into("<I", self, offset, value)

    result = None
    if isinstance(arg, int):
        result = OctetString([0] * arg)
    elif isinstance(arg, str):
        result = OctetString([ord(elem) for elem in arg])
    elif isinstance(arg, list):
        result = OctetString(arg)
    elif isinstance(arg, array):
        result = OctetString(arg)
    elif isinstance(arg, bytes):
        result = OctetString(arg)
    elif isinstance(arg, bytearray):
        result = OctetString(arg)

    def copy(self, dest_buffer, offset):
        for i in range(0, min(len(dest_buffer) - offset, len(self))):
            dest_buffer[offset + i] = self[i]

    def slice(list, start, end = None):
        if end == None:
            return buffer(list[start:])
        else:
            return buffer(list[start:end])

    def fill(list, value):
        for i in range(0, len(list)):
            list[i] = value

    bind(result, readUInt8)
    bind(result, readUInt8, 'readInt8')
    bind(result, readUInt16LE)
    bind(result, readUInt16BE)

    bind(result, writeUInt8)
    bind(result, writeUInt16LE)
    bind(result, writeUInt32LE)
    bind(result, writeUInt16BE)
    bind(result, copy)
    bind(result, slice)
    bind(result, fill)
    return result

def buffer_from_hex(hex):
    return buffer(bytearray.fromhex(hex))
    
class DotDict(dict):
    def __getattr__(self, key):
        return self[key] if key in self else None
    def __setattr__(self, key, val):
        if key in self.__dict__:
            self.__dict__[key] = val
        else:
            self[key] = val

    def __getitem__(self, row):
        return dict.__getitem__(self, row) if row in self else None

    def __delitem__(self, row):
        if row in self:
            dict.__delitem__(self, row)

class GrowingList(list):
    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([None]*(index + 1 - len(self)))
        list.__setitem__(self, index, value)

    def __getitem__(self, row):
        return list.__getitem__(self, row) if isinstance(row, slice) or row < len(self) else None

    def indexOf(self, item):
        try:
            return self.index(item)
        except:
            return -1

    def shift(self):
        if len(self) > 0:
            return self.pop()
        return None
# class os:
#     @staticmethod
#     def hostname():
#         return "unknown"

class Counter():
    def __init__(self, initial = 0):
        self._value = initial

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

    def preIncrement(self):
        self._value += 1
        return self._value

    def postIncrement(self):
        self._value += 1
        return self._value - 1

    def preDecrement(self):
        self._value -= 1
        return self._value

    def postDecrement(self):
        self._value -= 1
        return self._value + 1

class BufferEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, array):
        return base64.encodestring(obj)
    # Let the base class default method raise the TypeError
    return json.JSONEncoder.default(self, obj)

def arrayToHex(value):
    if value == None:
        return None
    value = [value] if not isinstance(value, array) else value
    return ''.join(format(x, '02x') for x in value)

def setTimeout(handler, delay):
    pass

def reverseAndReturn(list):
    list.reverse()
    return list

def indexOf(list, item):
    return list.index(item) if item in list else -1

def safehex(number):
    if isinstance(number, str):
        return number
    return hex(number)

def concat_lists(lists):
    return buffer([e for l in lists for e in l])

def ensureIsDotDict(x):
    if x:
        if isinstance(x, DotDict):
            return x
        elif isinstance(x, dict):
            return DotDict(x)
        else:
            raise 'argument must be a Dict or DotDict'
    else:
        return DotDict()
