from pybleno import *
from PizzaCrustCharacteristic import *
from PizzaToppingsCharacteristic import *
from PizzaBakeCharacteristic import *

class PizzaService(BlenoPrimaryService):
    def __init__(self, pizza):
        BlenoPrimaryService.__init__(self, {
          'uuid': '13333333333333333333333333333337',
          'characteristics': [
            PizzaCrustCharacteristic(pizza),
            PizzaToppingsCharacteristic(pizza),
            PizzaBakeCharacteristic(pizza)
          ]})