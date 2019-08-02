import sys
from bleno.supporting import *
bleno = require(__file__, '../..')
from bleno.supporting import *
math = require(__file__, 'math')
module = sys.modules[__name__]
util = require(__file__, '_util')
pizza = require(__file__, './pizza')

class PizzaToppingsCharacteristic(bleno.Characteristic):
  def __init__(self, pizza):
    bleno.Characteristic.__init__(self, DotDict([('uuid', '13333333333333333333333333330002'), ('properties', GrowingList(['read', 'write'])), ('descriptors', GrowingList([bleno.Descriptor(DotDict([('uuid', '2901'), ('value', 'Gets or sets the pizza toppings.')]))]))]))
    
    self.pizza = pizza
  
  def onWriteRequest(self, data, offset, withoutResponse, callback, *_varargs):
    if offset:
      callback(self.RESULT_ATTR_NOT_LONG)
    elif len(data) != 2:
      callback(self.RESULT_INVALID_ATTRIBUTE_LENGTH)
    else:
      
      self.pizza.toppings = data.readUInt16BE(0)
      callback(self.RESULT_SUCCESS)
  
  def onReadRequest(self, offset, callback, *_varargs2):
    if offset:
      callback(self.RESULT_ATTR_NOT_LONG, None)
    else:
      
      data = buffer(2)
      data.writeUInt16BE(self.pizza.toppings, 0)
      callback(self.RESULT_SUCCESS, data)

module.exports = PizzaToppingsCharacteristic
