import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:11 UTC
# source: /lib/bleno.js
# sha256: c8d91024a60a922cdab823807aceb17fee0a20251001391940c4ebce726056bd

math = require(__file__, 'math')
module = exports(__name__)
debug = require(__file__, '_debug')('bleno')

events = require(__file__, '_events')
os = require(__file__, '_os')
util = require(__file__, '_util')

UuidUtil = require(__file__, './uuid_util')

PrimaryService = require(__file__, './primary_service')
Characteristic = require(__file__, './characteristic')
Descriptor = require(__file__, './descriptor')

bindings = None

platform = os.platform()

if platform == 'darwin':
  bindings = require(__file__, './mac/bindings')
elif platform == 'linux' or platform == 'freebsd' or platform == 'win32' or platform == 'android':
  bindings = require(__file__, './hci_socket/bindings')
else:
  raise Error('Unsupported platform')

class Bleno(events.EventEmitter):
  def __init__(self, *varargs):
    events.EventEmitter.__init__(self)
    self.initialized = False
    self.platform = 'unknown'
    self.state = 'unknown'
    self.address = 'unknown'
    self.rssi = 0
    self.mtu = 20

    self._bindings = bindings

    self._bindings.on('stateChange', bind(self, self.onStateChange))
    self._bindings.on('platform', bind(self, self.onPlatform))
    self._bindings.on('addressChange', bind(self, self.onAddressChange))
    self._bindings.on('advertisingStart', bind(self, self.onAdvertisingStart))
    self._bindings.on('advertisingStop', bind(self, self.onAdvertisingStop))
    self._bindings.on('servicesSet', bind(self, self.onServicesSet))
    self._bindings.on('accept', bind(self, self.onAccept))
    self._bindings.on('mtuChange', bind(self, self.onMtuChange))
    self._bindings.on('disconnect', bind(self, self.onDisconnect))

    self._bindings.on('rssiUpdate', bind(self, self.onRssiUpdate))
    def _temp(self, event, *varargs):
      if event == 'stateChange' and not self.initialized:
        self._bindings.init()

        self.initialized = True
    self.on('newListener', bind(self, _temp))

  def onPlatform(self, platform, *varargs):
    debug('platform ' + str(platform))

    self.platform = platform

  def onStateChange(self, state, *varargs):
    debug('stateChange ' + str(state))

    self.state = state

    self.emit('stateChange', state)

  def onAddressChange(self, address, *varargs):
    debug('addressChange ' + str(address))

    self.address = address

  def onAccept(self, clientAddress, *varargs):
    debug('accept ' + str(clientAddress))
    self.emit('accept', clientAddress)

  def onMtuChange(self, mtu, *varargs):
    debug('mtu ' + str(mtu))

    self.mtu = mtu

    self.emit('mtuChange', mtu)

  def onDisconnect(self, clientAddress, *varargs):
    debug('disconnect ' + str(clientAddress))
    self.emit('disconnect', clientAddress)

  def startAdvertising(self, name, serviceUuids, callback=None, *varargs):
    if self.state != 'poweredOn':
      error = Error('Could not start advertising, state is ' + str(self.state) + ' (not poweredOn)')

      if is_callable(callback):
        callback(error)
      else:
        raise error

    else:
      if callback:
        self.once('advertisingStart', callback)

      undashedServiceUuids = GrowingList([])

      if serviceUuids and len(serviceUuids):
        i = 0
        while True:
          if not (i < len(serviceUuids)):
            break
          undashedServiceUuids[i] = UuidUtil.removeDashes(serviceUuids[i])
          i += 1

      self._bindings.startAdvertising(name, undashedServiceUuids)

  def startAdvertisingIBeacon(self, uuid, major, minor, measuredPower, callback=None, *varargs):
    if self.state != 'poweredOn':
      error = Error('Could not start advertising, state is ' + str(self.state) + ' (not poweredOn)')

      if is_callable(callback):
        callback(error)
      else:
        raise error

    else:
      undashedUuid = UuidUtil.removeDashes(uuid)
      uuidData = buffer_from_hex(undashedUuid)
      uuidDataLength = len(uuidData)
      iBeaconData = buffer(len(uuidData) + 5)

      i = 0
      while True:
        if not (i < uuidDataLength):
          break
        iBeaconData[i] = uuidData[i]
        i += 1

      iBeaconData.writeUInt16BE(major, uuidDataLength)
      iBeaconData.writeUInt16BE(minor, uuidDataLength + 2)
      iBeaconData.writeInt8(measuredPower, uuidDataLength + 4)

      if callback:
        self.once('advertisingStart', callback)

      debug('iBeacon data = ' + str(arrayToHex(iBeaconData)))

      self._bindings.startAdvertisingIBeacon(iBeaconData)

  def onAdvertisingStart(self, error=None, *varargs):
    debug('advertisingStart: ' + str(error))

    if error:
      self.emit('advertisingStartError', error)

    self.emit('advertisingStart', error)

  def startAdvertisingWithEIRData(self, advertisementData, scanData, callback=None, *varargs):
    if is_callable(scanData):
      callback = scanData
      scanData = None

    if self.state != 'poweredOn':
      error = Error('Could not advertising scanning, state is ' + str(self.state) + ' (not poweredOn)')

      if is_callable(callback):
        callback(error)
      else:
        raise error

    else:
      if callback:
        self.once('advertisingStart', callback)

      self._bindings.startAdvertisingWithEIRData(advertisementData, scanData)

  def stopAdvertising(self, callback=None, *varargs):
    if callback:
      self.once('advertisingStop', callback)
    self._bindings.stopAdvertising()

  def onAdvertisingStop(self, *varargs):
    debug('advertisingStop')
    self.emit('advertisingStop')

  def setServices(self, services, callback=None, *varargs):
    if callback:
      self.once('servicesSet', callback)
    self._bindings.setServices(services)

  def onServicesSet(self, error=None, *varargs):
    debug('servicesSet')

    if error:
      self.emit('servicesSetError', error)

    self.emit('servicesSet', error)

  def disconnect(self, *varargs):
    debug('disconnect')
    self._bindings.disconnect()

  def updateRssi(self, callback=None, *varargs):
    if callback:
      def _temp2(self, rssi, *varargs):
        callback(None, rssi)
      self.once('rssiUpdate', _temp2)

    self._bindings.updateRssi()

  def onRssiUpdate(self, rssi, *varargs):
    self.emit('rssiUpdate', rssi)

Bleno.PrimaryService = PrimaryService
Bleno.Characteristic = Characteristic
Bleno.Descriptor = Descriptor

module.exports = Bleno