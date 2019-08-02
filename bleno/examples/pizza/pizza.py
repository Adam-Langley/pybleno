import sys
import array
from bleno.supporting import *

bleno = require(__file__, '../..')

math = require(__file__, 'math')
module = sys.modules[__name__]
module.exports = DotDict()
util = require(__file__, '_util')
events = require(__file__, '_events')

PizzaCrust = DotDict([('NORMAL', 0), ('DEEP_DISH', 1), ('THIN', 2)])

PizzaToppings = DotDict([('NONE', 0), ('PEPPERONI', 1 << 0), ('MUSHROOMS', 1 << 1), ('EXTRA_CHEESE', 1 << 2), ('BLACK_OLIVES', 1 << 3), ('CANADIAN_BACON', 1 << 4), ('PINEAPPLE', 1 << 5), ('BELL_PEPPERS', 1 << 6), ('SAUSAGE', 1 << 7)])

PizzaBakeResult = DotDict([('HALF_BAKED', 0), ('BAKED', 1), ('CRISPY', 2), ('BURNT', 3), ('ON_FIRE', 4)])

class Pizza(events.EventEmitter):
  def __init__(self):
    events.EventEmitter.__init__(self)
    self.toppings = PizzaToppings.NONE
    self.crust = PizzaCrust.NORMAL
  
  def bake(self, temperature, *_varargs):
    time = temperature * 10
    self = self
    print('baking pizza at', temperature, 'degrees for', time, 'milliseconds')
    def _temp(*varargs):
      
      result = PizzaBakeResult.HALF_BAKED if (temperature < 350) else PizzaBakeResult.BAKED if (temperature < 450) else PizzaBakeResult.CRISPY if (temperature < 500) else PizzaBakeResult.BURNT if (temperature < 600) else PizzaBakeResult.ON_FIRE
      self.emit('ready', result)
    setTimeout(_temp, time)

module.exports.Pizza = Pizza
module.exports.PizzaToppings = PizzaToppings
module.exports.PizzaCrust = PizzaCrust
module.exports.PizzaBakeResult = PizzaBakeResult
