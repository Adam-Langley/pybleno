import sys
from bleno.supporting import *
bleno = require(__file__, '../..')
from bleno.supporting import *
import array
math = require(__file__, 'math')
module = sys.modules[__name__]
util = require(__file__, '_util')
pizza = require(__file__, './pizza')

class PizzaBakeCharacteristic(bleno.Characteristic):
  def __init__(self, pizza):
    bleno.Characteristic.__init__(self, DotDict([('uuid', '13333333333333333333333333330003'), ('properties', GrowingList(['notify', 'write'])), ('descriptors', GrowingList([bleno.Descriptor(DotDict([('uuid', '2901'), ('value', 'Bakes the pizza and notifies when done baking.')]))]))]))
    
    self.pizza = pizza
  
  def onWriteRequest(self, data, offset, withoutResponse, callback, *_varargs):
    if offset:
      callback(self.RESULT_ATTR_NOT_LONG)
    elif len(data) != 2:
      callback(self.RESULT_INVALID_ATTRIBUTE_LENGTH)
    else:
      
      temperature = data.readUInt16BE(0)
      self = self
      def _temp(result, *varargs):
        if self.updateValueCallback:
          data = buffer(1)
          data.writeUInt8(result, 0)
          self.updateValueCallback(data)
      self.pizza.once('ready', _temp)
      self.pizza.bake(temperature)
      callback(self.RESULT_SUCCESS)

module.exports = PizzaBakeCharacteristic
