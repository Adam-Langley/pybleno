import sys
from bleno.supporting import *
module = sys.modules[__name__]

math = require(__file__, 'math')
util = require(__file__, '_util')

#
# Require bleno peripheral library.
# https://github.com/sandeepmistry/bleno
#
bleno = require(__file__, '../..')

#
# Pizza
# * has crust
# * has toppings
# * can be baked
#
pizza = require(__file__, './pizza')

#
# The BLE Pizza Service!
#
PizzaService = require(__file__, './pizza_service')

#
# A name to advertise our Pizza Service.
#
name = 'PizzaSquat'
pizzaService = PizzaService(pizza.Pizza())
def _temp(state, *varargs):
  if state == 'poweredOn':
    def _temp3(err=None, *varargs):
      if err:
        print(err)
    #
    # We will also advertise the service ID in the advertising packet,
    # so it's easier to find.
    #
    bleno.startAdvertising(name, [pizzaService.uuid], _temp3)
  else:
    
    bleno.stopAdvertising()
#
# Wait until the BLE radio powers on before attempting to advertise.
# If you don't have a BLE radio, then it will never power on!
#
bleno.on('stateChange', _temp)
def _temp2(err=None, *varargs):
  if not err:
    print('advertising...') #
     # Once we are advertising, it's time to set up our services,
     # along with our characteristics.
     #
    
    #
    # Once we are advertising, it's time to set up our services,
    # along with our characteristics.
    #
    bleno.setServices([pizzaService])
bleno.on('advertisingStart', _temp2)

print ('Hit <ENTER> to disconnect')

if (sys.version_info > (3, 0)):
    input()
else:
    raw_input()

bleno.stopAdvertising()
bleno.disconnect()

print ('terminated.')
sys.exit(1)