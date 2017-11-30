from pybleno import *
import sys
import signal
from batteryservice import *

bleno = Bleno()

primaryService = BatteryService();

def onStateChange(state):
   print('on -> stateChange: ' + state);

   if (state == 'poweredOn'):
     bleno.startAdvertising('echo', ['ec00'])
   else:
     bleno.stopAdvertising();
bleno.on('stateChange', onStateChange)

def get_cellular_network():
    return "hello"

def set_cellular_network(value):
    print ("setting cell %d" % value)
    
    
def onAdvertisingStart(error):
    print('on -> advertisingStart: ' + ('error ' + error if error else 'success'));

    if not error:
        bleno.setServices([
            BlenoPrimaryService({
                'uuid': 'ec00',
                'characteristics': [ 
                    EchoCharacteristic('ec0F'),
                    LambdaCharacteristic('ec01', get_cellular_network, setter=set_cellular_network, description='Cellular Network')]
                    
            })
        ])
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
