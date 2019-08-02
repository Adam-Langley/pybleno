import sys
from bleno.supporting import *

bleno = require(__file__, '../..')
from bleno.supporting import *
import array
math = require(__file__, 'math')
module = sys.modules[__name__]
module.exports = DotDict()
util = require(__file__, '_util')

PizzaCrustCharacteristic = require(__file__, './pizza_crust_characteristic')
PizzaToppingsCharacteristic = require(__file__, './pizza_toppings_characteristic')
PizzaBakeCharacteristic = require(__file__, './pizza_bake_characteristic')

class PizzaService(bleno.PrimaryService):
  def __init__(self, pizza):
    bleno.PrimaryService.__init__(self, 
      {
        'uuid': '13333333333333333333333333333337',
        'characteristics': 
        [
          PizzaCrustCharacteristic(pizza), 
          PizzaToppingsCharacteristic(pizza), 
          PizzaBakeCharacteristic(pizza)
        ]
      })

module.exports = PizzaService
