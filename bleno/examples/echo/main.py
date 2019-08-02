import sys
from bleno.supporting import *

math = require(__file__, 'math')
module = sys.modules[__name__]
module.exports = DotDict()
bleno = require(__file__, '../..')

BlenoPrimaryService = bleno.PrimaryService

EchoCharacteristic = require(__file__, './characteristic')

print('bleno - echo')
def _temp(state, *varargs):
  print('on -> stateChange: ' + str(state))
  
  if state == 'poweredOn':
    bleno.startAdvertising('echo', GrowingList(['ec00']))
  else:
    bleno.stopAdvertising()
bleno.on('stateChange', _temp)
def _temp2(error, *varargs):
  print('on -> advertisingStart: ' + ('error ' + str(error) if error else 'success'))
  
  if not error:
    bleno.setServices(GrowingList([BlenoPrimaryService(DotDict([('uuid', 'ec00'), ('characteristics', GrowingList([EchoCharacteristic()]))]))]))
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