import sys
import os
from bleno.supporting import *

bleno = require(__file__, '../..')

BatteryService = require(__file__, './batteryservice')

primaryService = BatteryService()
def _temp(state):
  print('on -> stateChange: ' + str(state))

  if state == 'poweredOn':
    bleno.startAdvertising('Battery', [primaryService.uuid])
  else:
    bleno.stopAdvertising()
bleno.on('stateChange', _temp)
def _temp2(error=None):
  print('on -> advertisingStart: ' + ('error ' + str(error) if error else 'success'))
  
  if not error:
    def _temp3(error=None):
      print('setServices: ' + ('error ' + str(error) if error else 'success'))
    bleno.setServices([primaryService], _temp3)
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
