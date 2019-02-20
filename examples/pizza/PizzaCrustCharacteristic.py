from pybleno import *
import array
import struct
import sys
import traceback
from builtins import str
from Pizza import *

class PizzaCrustCharacteristic(Characteristic):
    
    def __init__(self, pizza):
        Characteristic.__init__(self, {
            'uuid': '13333333333333333333333333330001',
            'properties': ['read', 'write'],
            'descriptors': [
                    Descriptor(
                        uuid = '2901',
                        value = 'Gets or sets the type of pizza crust.'
                    )],   
            'value': None
          })
          
        self.pizza = pizza
          
    def onReadRequest(self, offset, callback):
        
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = array.array('B', [0] * 1)
            writeUInt8(data, self.pizza.crust, 0)
            callback(Characteristic.RESULT_SUCCESS, data);

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        elif len(data) != 1:
            callback(Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH)
        else:
            crust = readUInt8(data, 0)
            if crust == PizzaCrust['NORMAL'] or crust == PizzaCrust['DEEP_DISH'] or crust == PizzaCrust['THIN']:
                self.pizza.crust = crust
                callback(Characteristic.RESULT_SUCCESS);
            else:
                callback(Characteristic.RESULT_UNLIKELY_ERROR);
