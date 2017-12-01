from pybleno import *
import sys
import signal
from BatteryService import *

bleno = Bleno()

primaryService = BatteryService();

def onStateChange(state):
   print('on -> stateChange: ' + state);

   if (state == 'poweredOn'):
       bleno.startAdvertising('Battery', [primaryService.uuid]);
   else:
     bleno.stopAdvertising();
bleno.on('stateChange', onStateChange)

def onAdvertisingStart(error):
    print('on -> advertisingStart: ' + ('error ' + error if error else 'success'));

    if not error:
        def on_setServiceError(error):
            print('setServices: %s'  % ('error ' + error if error else 'success'))
            
        bleno.setServices([
            primaryService
        ], on_setServiceError)
bleno.on('advertisingStart', onAdvertisingStart)

print ('Hit <ENTER> to disconnect')

if (sys.version_info > (3, 0)):
    input()
else:
    raw_input()

bleno.stopAdvertising()
bleno.disconnect()

print ('terminated.')
sys.exit(1)
