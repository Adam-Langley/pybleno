from pybleno import *
import array
import struct
import sys
import traceback
from builtins import str

class PizzaBakeCharacteristic(Characteristic):
    
    def __init__(self, pizza):
        Characteristic.__init__(self, {
            'uuid': '13333333333333333333333333330003',
            'properties': ['notify', 'write'],
            'descriptors': [
                    Descriptor(
                        uuid = '2901',
                        value ='Bakes the pizza and notifies when done baking.'
                    )],   
            'value': None
          })
          
        self.pizza = pizza
        self.updateValueCallback = None

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        elif len(data) != 2:
            callback(Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH)
        else:
            temperature = readUInt16BE(data, 0)
            def on_pizzaReady(result):
                print ('pizza is ready!')
                if self.updateValueCallback:
                    data = array.array('B', [0] * 1)
                    writeUInt8(data, result, 0);
                    self.updateValueCallback(data)
            self.pizza.once('ready', [], on_pizzaReady)
            self.pizza.bake(temperature)
            callback(Characteristic.RESULT_SUCCESS)
