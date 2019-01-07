from pybleno import *
import sys
import signal

bleno = Bleno()

#
# Pizza
# * has crust
# * has toppings
# * can be baked
#
from Pizza import *


#
# The BLE Pizza Service!
#
from PizzaService import *

#
# A name to advertise our Pizza Service.
#
name = 'PizzaSquat'
pizzaService = PizzaService(Pizza())

#
# Wait until the BLE radio powers on before attempting to advertise.
# If you don't have a BLE radio, then it will never power on!
#
def onStateChange(state):
    if (state == 'poweredOn'):
        #
        # We will also advertise the service ID in the advertising packet,
        # so it's easier to find.
        #
        def on_startAdvertising(err):
            if err:
                print(err)

        bleno.startAdvertising(name, [pizzaService.uuid], on_startAdvertising)
    else:
        bleno.stopAdvertising();
bleno.on('stateChange', onStateChange)
    
def onAdvertisingStart(error):
    if not error:
        print('advertising...')
        #
        # Once we are advertising, it's time to set up our services,
        # along with our characteristics.
        #        
        bleno.setServices([
            pizzaService
        ])
bleno.on('advertisingStart', onAdvertisingStart)

bleno.start()

print ('Hit <ENTER> to disconnect')

if (sys.version_info > (3, 0)):
    input()
else:
    raw_input()

bleno.stopAdvertising()
bleno.disconnect()

print ('terminated.')
sys.exit(1)
