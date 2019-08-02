import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:13 UTC
# source: /lib/hci-socket/bindings.js
# sha256: a633ce7587eb1c384f3a0071583d0706e8194c51b7cb864823d079a4365b8e68

math = require(__file__, 'math')
module = exports(__name__)
debug = require(__file__, '_debug')('bindings')

events = require(__file__, '_events')
util = require(__file__, '_util')
os = require(__file__, '_os')

AclStream = require(__file__, './acl_stream')
Hci = require(__file__, './hci')
Gap = require(__file__, './gap')
Gatt = require(__file__, './gatt')

class BlenoBindings(events.EventEmitter):
  def __init__(self, *varargs):
    events.EventEmitter.__init__(self)
    self._state = None

    self._advertising = False

    self._hci = Hci()
    self._gap = Gap(self._hci)
    self._gatt = Gatt(self._hci)

    self._address = None
    self._handle = None
    self._aclStream = None

  def startAdvertising(self, name, serviceUuids, *varargs):
    self._advertising = True

    self._gap.startAdvertising(name, serviceUuids)

  def startAdvertisingIBeacon(self, data, *varargs):
    self._advertising = True

    self._gap.startAdvertisingIBeacon(data)

  def startAdvertisingWithEIRData(self, advertisementData, scanData, *varargs):
    self._advertising = True

    self._gap.startAdvertisingWithEIRData(advertisementData, scanData)

  def stopAdvertising(self, *varargs):
    self._advertising = False

    self._gap.stopAdvertising()

  def setServices(self, services, *varargs):
    self._gatt.setServices(services)

    self.emit('servicesSet')

  def disconnect(self, *varargs):
    if self._handle:
      debug('disconnect by server')

      self._hci.disconnect(self._handle)

  def updateRssi(self, *varargs):
    if self._handle:
      self._hci.readRssi(self._handle)

  def init(self, *varargs):
    self.onSigIntBinded = bind(self, self.onSigInt)

    process.on('SIGINT', self.onSigIntBinded)
    process.on('exit', bind(self, self.onExit))

    self._gap.on('advertisingStart', bind(self, self.onAdvertisingStart))
    self._gap.on('advertisingStop', bind(self, self.onAdvertisingStop))

    self._gatt.on('mtuChange', bind(self, self.onMtuChange))

    self._hci.on('stateChange', bind(self, self.onStateChange))
    self._hci.on('addressChange', bind(self, self.onAddressChange))
    self._hci.on('readLocalVersion', bind(self, self.onReadLocalVersion))

    self._hci.on('leConnComplete', bind(self, self.onLeConnComplete))
    self._hci.on('leConnUpdateComplete', bind(self, self.onLeConnUpdateComplete))
    self._hci.on('rssiRead', bind(self, self.onRssiRead))
    self._hci.on('disconnComplete', bind(self, self.onDisconnComplete))
    self._hci.on('encryptChange', bind(self, self.onEncryptChange))
    self._hci.on('leLtkNegReply', bind(self, self.onLeLtkNegReply))
    self._hci.on('aclDataPkt', bind(self, self.onAclDataPkt))

    self.emit('platform', os.platform())

    self._hci.init()

  def onStateChange(self, state, *varargs):
    if self._state == state:
      return
    self._state = state

    if state == 'unauthorized':
      print('bleno warning: adapter state unauthorized, please run as root or with sudo')
      print('               or see README for information on running without root/sudo:')
      print('               https://github.com/sandeepmistry/bleno#running-on-linux')
    elif state == 'unsupported':
      print('bleno warning: adapter does not support Bluetooth Low Energy (BLE, Bluetooth Smart).')
      print('               Try to run with environment variable:')
      print('               [sudo] BLENO_HCI_DEVICE_ID=x node ...')

    self.emit('stateChange', state)

  def onAddressChange(self, address, *varargs):
    self.emit('addressChange', address)

  def onReadLocalVersion(self, hciVer, hciRev, lmpVer, manufacturer, lmpSubVer, *varargs):
    pass

  def onAdvertisingStart(self, error, *varargs):
    self.emit('advertisingStart', error)

  def onAdvertisingStop(self, *varargs):
    self.emit('advertisingStop')

  def onLeConnComplete(self, status, handle, role, addressType, address, interval, latency, supervisionTimeout, masterClockAccuracy, *varargs):
    if role != 1:
      # not slave, ignore
      return

    self._address = address
    self._handle = handle
    self._aclStream = AclStream(self._hci, handle, self._hci.addressType, self._hci.address, addressType, address)
    self._gatt.setAclStream(self._aclStream)

    self.emit('accept', address)

  def onLeConnUpdateComplete(self, handle, interval, latency, supervisionTimeout, *varargs):
    pass

  def onDisconnComplete(self, handle, reason, *varargs):
    if self._aclStream:
      self._aclStream.push(None, None)

    address = self._address

    self._address = None
    self._handle = None
    self._aclStream = None

    if address:
      self.emit('disconnect', address) # TODO: use reason

    if self._advertising:
      self._gap.restartAdvertising()

  def onEncryptChange(self, handle, encrypt, *varargs):
    if self._handle == handle and self._aclStream:
      self._aclStream.pushEncrypt(encrypt)

  def onLeLtkNegReply(self, handle, *varargs):
    if self._handle == handle and self._aclStream:
      self._aclStream.pushLtkNegReply()

  def onMtuChange(self, mtu, *varargs):
    self.emit('mtuChange', mtu)

  def onRssiRead(self, handle, rssi, *varargs):
    self.emit('rssiUpdate', rssi)

  def onAclDataPkt(self, handle, cid, data, *varargs):
    if self._handle == handle and self._aclStream:
      self._aclStream.push(cid, data)

  def onSigInt(self, *varargs):
    sigIntListeners = process.listeners('SIGINT')

    if sigIntListeners[len(sigIntListeners) - 1] == self.onSigIntBinded:
      # we are the last listener, so exit
      # this will trigger onExit, and clean up
      process.exit(1)

  def onExit(self, *varargs):
    self._gap.stopAdvertising()

    self.disconnect()

module.exports = BlenoBindings()