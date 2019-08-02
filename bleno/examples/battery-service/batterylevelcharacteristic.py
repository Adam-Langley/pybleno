import sys
import os
from os import path
from bleno.supporting import *

module = sys.modules[__name__]

bleno = require(__file__, '../..')

os = require(__file__, '_os')

Descriptor = bleno.Descriptor
Characteristic = bleno.Characteristic

class BatteryLevelCharacteristic(Characteristic):
  def __init__(self, *_varargs):
    Characteristic.__init__(self, {
      'uuid': '2A19', 
      'properties': ['read'],
      'descriptors': [
        Descriptor({'uuid': '2901', 'value': 'Battery level between 0 and 100 percent'}), 
        Descriptor({'uuid': '2904', 'value': buffer([0x04, 0x01, 0x27, 0xAD, 0x01, 0x00, 0x00])})
      ]})
  
  def onReadRequest(self, offset, callback, *_varargs2):
    if os.platform() == 'darwin':
      def _temp(self, error, stdout, stderr):
        data = stdout.toString()
        # data - 'Now drawing from \'Battery Power\'\n -InternalBattery-0\t95%; discharging; 4:11 remaining\n'
        percent = data.split('	')[1].split(';')[0]
        print(percent)
        percent = parseInt(percent, 10)
        callback(self.RESULT_SUCCESS, [percent])
      exec('pmset -g batt', _temp)
      _temp(self, None, 'Now drawing from \'Battery Power\'\n -InternalBattery-0\t95%; discharging; 4:11 remaining\n', None)
    else:
      print('returning hardcoded value...')
      # return hardcoded value
      callback(self.RESULT_SUCCESS, [98])

module.exports = BatteryLevelCharacteristic
