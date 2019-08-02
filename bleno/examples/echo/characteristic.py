import array
import struct
import sys
import traceback
from builtins import str

from bleno.supporting import *

bleno = require(__file__, '../..')

module = sys.modules[__name__]

BlenoCharacteristic = bleno.Characteristic;

class EchoCharacteristic(BlenoCharacteristic):
    
    def __init__(self):
        BlenoCharacteristic.__init__(self, {
            'uuid': 'ec0e',
            'properties': ['read', 'write', 'notify'],
#            'secure': ['read', 'write', 'notify'],
            'value': None
          })
          
        self._value = buffer(0)
        self._updateValueCallback = None
          
    def onReadRequest(self, offset, callback):
        print('EchoCharacteristic - %s - onReadRequest: value = %s' % (self['uuid'], bytes(self._value).hex()))
        callback(self.RESULT_SUCCESS, self._value[offset:])

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data

        print('EchoCharacteristic - %s - onWriteRequest: value = %s' % (self['uuid'], bytes(self._value).hex()))

        if self._updateValueCallback:
            print('EchoCharacteristic - onWriteRequest: notifying');
            
            self._updateValueCallback(self._value)
        
        callback(self.RESULT_SUCCESS)
        
    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('EchoCharacteristic - onSubscribe')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('EchoCharacteristic - onUnsubscribe');
        
        self._updateValueCallback = None

module.exports = EchoCharacteristic