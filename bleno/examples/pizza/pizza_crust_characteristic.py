import sys
from bleno.supporting import *

bleno = require(__file__, '../..')
from bleno.supporting import *
import array
math = require(__file__, 'math')
module = sys.modules[__name__]
util = require(__file__, '_util')
pizza = require(__file__, './pizza')

class PizzaCrustCharacteristic(bleno.Characteristic):
  def __init__(self, pizza):
    bleno.Characteristic.__init__(self, DotDict([('uuid', '13333333333333333333333333330001'), ('properties', GrowingList(['read', 'write'])), ('descriptors', GrowingList([bleno.Descriptor(DotDict([('uuid', '2901'), ('value', 'Gets or sets the type of pizza crust.')]))]))]))
    
    self.pizza = pizza
  
  def onWriteRequest(self, data, offset, withoutResponse, callback, *_varargs):
    if offset:
      callback(self.RESULT_ATTR_NOT_LONG)
    elif len(data) != 1:
      callback(self.RESULT_INVALID_ATTRIBUTE_LENGTH)
    else:
      
      crust = data.readUInt8(0)
      for _temp in switch(crust):
        if _temp(pizza.PizzaCrust.NORMAL):
          pass
        if _temp(pizza.PizzaCrust.NORMAL) or _temp(pizza.PizzaCrust.DEEP_DISH):
          pass
        if _temp(pizza.PizzaCrust.NORMAL) or _temp(pizza.PizzaCrust.DEEP_DISH) or _temp(pizza.PizzaCrust.NORMAL) or _temp(pizza.PizzaCrust.THIN):
          self.pizza.crust = crust
          callback(self.RESULT_SUCCESS)
          break
        if _temp(True):
          
          callback(self.RESULT_UNLIKELY_ERROR)
          break
  
  def onReadRequest(self, offset, callback, *_varargs2):
    if offset:
      callback(self.RESULT_ATTR_NOT_LONG, None)
    else:
      
      data = buffer(1)
      data.writeUInt8(self.pizza.crust, 0)
      callback(self.RESULT_SUCCESS, data)

module.exports = PizzaCrustCharacteristic
