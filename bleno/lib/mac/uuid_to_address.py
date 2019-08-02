import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:12 UTC
# source: /lib/mac/uuid-to-address.js
# sha256: be7896572f1abca7514003d1ac606aecb5bb50a0264ce117f1f42d041899d972

math = require(__file__, 'math')
module = exports(__name__)
bplist = require(__file__, 'bplist_parser')
def _temp(uuid, callback, *varargs):
  def _temp2(err, obj, *varargs):
    if err:
      return callback(err)
    elif obj[0].CoreBluetoothCache == None:
      return callback(Error('Empty CoreBluetoothCache entry!'))

    uuid = uuid.toUpperCase()

    formattedUuid = str(uuid.substring(0, 8)) + '-' + str(uuid.substring(8, 12)) + '-' + str(uuid.substring(12, 16)) + '-' + str(uuid.substring(16, 20)) + '-' + uuid.substring(20)

    coreBluetoothCacheEntry = obj[0].CoreBluetoothCache[formattedUuid]
    address = re.sub('-', ':', coreBluetoothCacheEntry.DeviceAddress) if coreBluetoothCacheEntry else None

    callback(None, address)
  bplist.parseFile('/Library/Preferences/com.apple.Bluetooth.plist', _temp2)
module.exports = _temp