from pybleno import *
import array
import sys
import subprocess
import re

class BatteryLevelCharacteristic(Characteristic):
    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': '2A19',
            'properties': ['read'],
            'value': None,
            'descriptors': [
                  Descriptor({
                    'uuid': '2901',
                    'value': 'Battery level between 0 and 100 percent'
                  }),
                  Descriptor({
                    'uuid': '2904',
                    'value': array.array('B', [0x04, 0x01, 0x27, 0xAD, 0x01, 0x00, 0x00 ]) # maybe 12 0xC unsigned 8 bit
                  })
                ]            
          })
          
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
          
    def onReadRequest(self, offset, callback):
        if sys.platform == 'darwin':
        	output = subprocess.check_output("pmset -g batt", shell=True)
        	result = {}
        	for row in output.split('\n'):
        		if 'InternalBatter' in row:
        			percent = row.split('\t')[1].split(';')[0];
        			percent = int(re.findall('\d+', percent)[0]);
        			callback(Characteristic.RESULT_SUCCESS, array.array('B', [percent]))
        			break
        else:
            # return hardcoded value
            callback(Characteristic.RESULT_SUCCESS, array.array('B', [98]))
