import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:14 UTC
# source: /lib/hci-socket/gap.js
# sha256: 13482150c7184c7f61afbbb9669f3a47ba88ff3498ad30df217721aee62db947

require(__file__, 'json')
math = require(__file__, 'math')
module = exports(__name__)
debug = require(__file__, '_debug')('gap')

events = require(__file__, '_events')
os = require(__file__, '_os')
util = require(__file__, '_util')

Hci = require(__file__, './hci')

isLinux = (os.platform() == 'linux')
isIntelEdison = isLinux and (indexOf(os.release(), 'edison') != -1)
isYocto = isLinux and (indexOf(os.release(), 'yocto') != -1)

class Gap(events.EventEmitter):
  def __init__(self, hci, *varargs):
    events.EventEmitter.__init__(self)
    self._hci = hci

    self._advertiseState = None

    self._hci.on('error', bind(self, self.onHciError))

    self._hci.on('leAdvertisingParametersSet', bind(self, self.onHciLeAdvertisingParametersSet))
    self._hci.on('leAdvertisingDataSet', bind(self, self.onHciLeAdvertisingDataSet))
    self._hci.on('leScanResponseDataSet', bind(self, self.onHciLeScanResponseDataSet))
    self._hci.on('leAdvertiseEnableSet', bind(self, self.onHciLeAdvertiseEnableSet))

  def startAdvertising(self, name, serviceUuids, *varargs):
    debug('startAdvertising: name = ' + str(name) + ', serviceUuids = ' + json.dumps(serviceUuids, indent = 4))

    advertisementDataLength = 3
    scanDataLength = 0

    serviceUuids16bit = GrowingList([])
    serviceUuids128bit = GrowingList([])
    i = 0

    if name and len(name):
      scanDataLength += 2 + len(name)

    if serviceUuids and len(serviceUuids):
      i = 0
      while True:
        if not (i < len(serviceUuids)):
          break
        serviceUuid = buffer_from_hex(''.join(reverseAndReturn(re.findall('.{1,2}', serviceUuids[i]))))

        if len(serviceUuid) == 2:
          serviceUuids16bit.append(serviceUuid)
        elif len(serviceUuid) == 16:
          serviceUuids128bit.append(serviceUuid)
        i += 1

    if len(serviceUuids16bit):
      advertisementDataLength += 2 + 2 * len(serviceUuids16bit)

    if len(serviceUuids128bit):
      advertisementDataLength += 2 + 16 * len(serviceUuids128bit)

    advertisementData = buffer(advertisementDataLength)
    scanData = buffer(scanDataLength)

    # flags
    advertisementData.writeUInt8(2, 0)
    advertisementData.writeUInt8(0x01, 1)
    advertisementData.writeUInt8(0x06, 2)

    advertisementDataOffset = 3

    if len(serviceUuids16bit):
      advertisementData.writeUInt8(1 + 2 * len(serviceUuids16bit), advertisementDataOffset)
      advertisementDataOffset += 1

      advertisementData.writeUInt8(0x03, advertisementDataOffset)
      advertisementDataOffset += 1
      i = 0
      while True:
        if not (i < len(serviceUuids16bit)):
          break
        serviceUuids16bit[i].copy(advertisementData, advertisementDataOffset)
        advertisementDataOffset += len(serviceUuids16bit[i])
        i += 1

    if len(serviceUuids128bit):
      advertisementData.writeUInt8(1 + 16 * len(serviceUuids128bit), advertisementDataOffset)
      advertisementDataOffset += 1

      advertisementData.writeUInt8(0x06, advertisementDataOffset)
      advertisementDataOffset += 1
      i = 0
      while True:
        if not (i < len(serviceUuids128bit)):
          break
        serviceUuids128bit[i].copy(advertisementData, advertisementDataOffset)
        advertisementDataOffset += len(serviceUuids128bit[i])
        i += 1

    # name
    if name and len(name):
      nameBuffer = buffer(name)

      scanData.writeUInt8(1 + len(nameBuffer), 0)
      scanData.writeUInt8(0x08, 1)
      nameBuffer.copy(scanData, 2)

    self.startAdvertisingWithEIRData(advertisementData, scanData)

  def startAdvertisingIBeacon(self, data, *varargs):
    debug('startAdvertisingIBeacon: data = ' + str(arrayToHex(data)))

    dataLength = len(data)
    manufacturerDataLength = 4 + dataLength
    advertisementDataLength = 5 + manufacturerDataLength
    scanDataLength = 0

    advertisementData = buffer(advertisementDataLength)
    scanData = buffer(0)

    # flags
    advertisementData.writeUInt8(2, 0)
    advertisementData.writeUInt8(0x01, 1)
    advertisementData.writeUInt8(0x06, 2)

    advertisementData.writeUInt8(manufacturerDataLength + 1, 3)
    advertisementData.writeUInt8(0xff, 4)
    advertisementData.writeUInt16LE(0x004c, 5) # Apple Company Identifier LE (16 bit)
    advertisementData.writeUInt8(0x02, 7) # type, 2 => iBeacon
    advertisementData.writeUInt8(dataLength, 8)

    data.copy(advertisementData, 9)

    self.startAdvertisingWithEIRData(advertisementData, scanData)

  def startAdvertisingWithEIRData(self, advertisementData=None, scanData=None, *varargs):
    advertisementData = advertisementData or buffer(0)
    scanData = scanData or buffer(0)

    debug('startAdvertisingWithEIRData: advertisement data = ' + str(arrayToHex(advertisementData)) + ', scan data = ' + arrayToHex(scanData))

    error = None

    if len(advertisementData) > 31:
      error = Error('Advertisement data is over maximum limit of 31 bytes')
    elif len(scanData) > 31:
      error = Error('Scan data is over maximum limit of 31 bytes')

    if error:
      self.emit('advertisingStart', error)
    else:
      self._advertiseState = 'starting'

      if isIntelEdison or isYocto:
        # work around for Intel Edison
        debug('skipping first set of scan response and advertisement data')
      else:
        self._hci.setScanResponseData(scanData)
        self._hci.setAdvertisingData(advertisementData)
      self._hci.setAdvertiseEnable(True)
      self._hci.setScanResponseData(scanData)
      self._hci.setAdvertisingData(advertisementData)

  def restartAdvertising(self, *varargs):
    self._advertiseState = 'restarting'

    self._hci.setAdvertiseEnable(True)

  def stopAdvertising(self, *varargs):
    self._advertiseState = 'stopping'

    self._hci.setAdvertiseEnable(False)

  def onHciError(self, error, *varargs):
    pass

  def onHciLeAdvertisingParametersSet(self, status, *varargs):
    pass

  def onHciLeAdvertisingDataSet(self, status, *varargs):
    pass

  def onHciLeScanResponseDataSet(self, status, *varargs):
    pass

  def onHciLeAdvertiseEnableSet(self, status=None, *varargs):
    if self._advertiseState == 'starting':
      self._advertiseState = 'started'

      error = None

      if status:
        error = Error(Hci.STATUS_MAPPER[status] or ('Unknown (' + str(status) + ')'))

      self.emit('advertisingStart', error)
    elif self._advertiseState == 'stopping':
      self._advertiseState = 'stopped'

      self.emit('advertisingStop')

module.exports = Gap