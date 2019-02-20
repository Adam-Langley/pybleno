from pybleno import *
import array
import struct
import sys
import traceback
from builtins import str

class PizzaToppingsCharacteristic(Characteristic):
    
    def __init__(self, pizza):
        Characteristic.__init__(self, {
            'uuid': '13333333333333333333333333330002',
            'properties': ['read', 'write'],
            'descriptors': [
                    Descriptor(
                        uuid = '2901',
                        value = 'Gets or sets the pizza toppings.'
                    )],   
            'value': None
          })
          
        self.pizza = pizza
          
    def onReadRequest(self, offset, callback):
        
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = array.array('B', [0] * 2)
            writeUInt8(data, self.pizza.toppings, 0)
            callback(Characteristic.RESULT_SUCCESS, data);

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        elif len(data) != 2:
            callback(Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH)
        else:
            self.pizza.toppings = readUInt16BE(data, 0)
            callback(Characteristic.RESULT_SUCCESS);
