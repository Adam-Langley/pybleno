import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:12 UTC
# source: /lib/mac/yosemite.js
# sha256: bd31413ca150529d787aec2b3a9918ff7d28fb0e3bd8ad44ab166a44563cf5b5

require(__file__, 'json')
math = require(__file__, 'math')
module = exports(__name__)# jshint loopfunc: true
debug = require(__file__, '_debug')('yosemite-bindings')

child_process = require(__file__, '_child_process')
events = require(__file__, '_events')
os = require(__file__, '_os')
util = require(__file__, '_util')

XpcConnection = require(__file__, '_xpc_connection')

uuidToAddress = require(__file__, './uuid_to_address')

osRelease = parseFloat(os.release())

class BlenoBindings(events.EventEmitter):
  def __init__(self, *varargs):
    events.EventEmitter.__init__(self)
    self._xpcConnection = XpcConnection('com.apple.blued')
    self._deviceUUID = None
    def _temp(self, message, *varargs):
      self.emit('xpcError', message)
    self._xpcConnection.on('error', bind(self, _temp))
    def _temp2(self, event, *varargs):
      self.emit('xpcEvent', event)
    self._xpcConnection.on('event', bind(self, _temp2))

  def sendXpcMessage(self, message, *varargs):
    self._xpcConnection.sendMessage(message)

  def disconnect(self, *varargs):
    raise Error('disconnect is not supported on OS X!')

blenoBindings = BlenoBindings()
def _temp3(event, *varargs):
  kCBMsgId = event.kCBMsgId
  kCBMsgArgs = event.kCBMsgArgs

  debug('xpcEvent: ' + str(json.dumps(event, indent = 4)))

  self.emit('kCBMsgId' + str(kCBMsgId), kCBMsgArgs)
blenoBindings.on('xpcEvent', _temp3)
def _temp4(message, *varargs):
  console.error('xpcError: ' + str(message))
blenoBindings.on('xpcError', _temp4)
def _temp5(id, args, *varargs):
  debug('sendCBMsg: ' + str(id) + ', ' + json.dumps(args, indent = 4))
  self.sendXpcMessage(DotDict([
    ('kCBMsgId', id),
    ('kCBMsgArgs', args)
  ]))
blenoBindings.sendCBMsg = _temp5
def _temp6(*varargs):
  self._xpcConnection.setup()
  def _temp24(error, stdout, stderr, *varargs):
    self.emit('platform', os.platform())

    if not error:
      found = re.findall('\s+Address: (.*)', stdout)
      if found:
        address = re.sub('-', ':', found[1].toLowerCase())

        self.emit('addressChange', address)

    if osRelease < 13:
      debug('bleno warning: OS X < 10.9 detected')

      console.warn('bleno requires OS X 10.9 or higher!')

      self.emit('stateChange', 'unsupported')
    else:
      self.sendCBMsg(1, DotDict([
        ('kCBMsgArgName', 'node-' + str((Date()).getTime())),
        ('kCBMsgArgOptions', DotDict([
          ('kCBInitOptionShowPowerAlert', 1)
        ])),
        ('kCBMsgArgType', 1)
      ]))
  child_process.exec('system_profiler SPBluetoothDataType', DotDict([]), bind(self, _temp24))
blenoBindings.init = _temp6
def _temp7(args, *varargs):
  state = GrowingList(['unknown', 'resetting', 'unsupported', 'unauthorized', 'poweredOff', 'poweredOn'])[args.kCBMsgArgState]
  debug('state change ' + str(state))
  self.emit('stateChange', state)
blenoBindings.on('kCBMsgId6', _temp7)
def _temp8(name, serviceUuids, *varargs):
  advertisement = DotDict([
    ('kCBAdvDataLocalName', name),
    ('kCBAdvDataServiceUUIDs', GrowingList([]))
  ])

  if serviceUuids and len(serviceUuids):
    i = 0
    while True:
      if not (i < len(serviceUuids)):
        break
      advertisement.kCBAdvDataServiceUUIDs[i] = buffer_from_hex(serviceUuids[i])
      i += 1

  self.sendCBMsg(8, advertisement)
blenoBindings.startAdvertising = _temp8
def _temp9(data, *varargs):
  args = DotDict([])

  if osRelease >= 14:
    args.kCBAdvDataAppleMfgData = concat_lists(GrowingList([buffer(
      GrowingList([len(data) + 5, 0xff, 0x4c, 0x00, 0x02, len(data)])), 
      data
    ]))
  else:
    args.kCBAdvDataAppleBeaconKey = data

  self.sendCBMsg(8, args)
blenoBindings.startAdvertisingIBeacon = _temp9
def _temp10(advertisementData, *varargs):
  if osRelease < 14:
    raise Error('startAdvertisingWithEIRData is only supported on OS X 10.10 and above!')

  self.sendCBMsg(8, DotDict([
    ('kCBAdvDataAppleMfgData', advertisementData)
  ]))
blenoBindings.startAdvertisingWithEIRData = _temp10
def _temp11(args, *varargs):
  result = args.kCBMsgArgResult
  error = None

  if result:
    error = Error('Unknown error (result ' + str(result) + ')')

  self.emit('advertisingStart', error)
blenoBindings.on('kCBMsgId16', _temp11)
def _temp12(*varargs):
  self.sendCBMsg(9, None)
blenoBindings.stopAdvertising = _temp12
def _temp13(args, *varargs):
  self.emit('advertisingStop')
blenoBindings.on('kCBMsgId17', _temp13)
def _temp14(services, *varargs):
  self.sendCBMsg(12, None) # remove all services

  services = services or GrowingList([])
  attributeId = 1

  self._attributes = GrowingList([])
  self._setServicesError = None

  if len(services):
    i = 0
    while True:
      if not (i < len(services)):
        break
      service = services[i]

      arg = DotDict([
        ('kCBMsgArgAttributeID', attributeId),
        ('kCBMsgArgAttributeIDs', GrowingList([])),
        ('kCBMsgArgCharacteristics', GrowingList([])),
        ('kCBMsgArgType', 1), # 1 => primary, 0 => included
        ('kCBMsgArgUUID', buffer_from_hex(service.uuid))
      ])

      self._attributes[attributeId] = service

      self._lastServiceAttributeId = attributeId
      attributeId += 1

      j = 0
      while True:
        if not (j < len(service.characteristics)):
          break
        characteristic = service.characteristics[j]

        properties = 0
        permissions = 0

        if indexOf(characteristic.properties, 'read') != -1:
          properties |= 0x02

          if indexOf(characteristic.secure, 'read') != -1:
            permissions |= 0x04
          else:
            permissions |= 0x01

        if indexOf(characteristic.properties, 'writeWithoutResponse') != -1:
          properties |= 0x04

          if indexOf(characteristic.secure, 'writeWithoutResponse') != -1:
            permissions |= 0x08
          else:
            permissions |= 0x02

        if indexOf(characteristic.properties, 'write') != -1:
          properties |= 0x08

          if indexOf(characteristic.secure, 'write') != -1:
            permissions |= 0x08
          else:
            permissions |= 0x02

        if indexOf(characteristic.properties, 'notify') != -1:
          if indexOf(characteristic.secure, 'notify') != -1:
            properties |= 0x100
          else:
            properties |= 0x10

        if indexOf(characteristic.properties, 'indicate') != -1:
          if indexOf(characteristic.secure, 'indicate') != -1:
            properties |= 0x200
          else:
            properties |= 0x20

        characteristicArg = DotDict([
          ('kCBMsgArgAttributeID', attributeId),
          ('kCBMsgArgAttributePermissions', permissions),
          ('kCBMsgArgCharacteristicProperties', properties),
          ('kCBMsgArgData', characteristic.value),
          ('kCBMsgArgDescriptors', GrowingList([])),
          ('kCBMsgArgUUID', buffer_from_hex(characteristic.uuid))
        ])

        self._attributes[attributeId] = characteristic

        k = 0
        while True:
          if not (k < len(characteristic.descriptors)):
            break
          descriptor = characteristic.descriptors[k]

          characteristicArg.kCBMsgArgDescriptors.append(DotDict([
            ('kCBMsgArgData', descriptor.value),
            ('kCBMsgArgUUID', buffer_from_hex(descriptor.uuid))
          ]))
          k += 1

        arg.kCBMsgArgCharacteristics.append(characteristicArg)

        attributeId += 1
        j += 1

      self.sendCBMsg(10, arg)
      i += 1
  else:
    self.emit('servicesSet')
blenoBindings.setServices = _temp14
def _temp15(*varargs):
  if self._deviceUUID == None:
    self.emit('rssiUpdate', 127) # not supported

  else:
    self.sendCBMsg(44, DotDict([
      ('kCBMsgArgDeviceUUID', self._deviceUUID)
    ]))
blenoBindings.updateRssi = _temp15
def _temp16(args, *varargs):
  attributeId = args.kCBMsgArgAttributeID
  result = args.kCBMsgArgResult

  if result:
    errorMessage = 'failed to set service ' + str(self._attributes[attributeId].uuid)

    if result == 27:
      errorMessage += ', UUID not allowed!'

    self._setServicesError = Error(errorMessage)

  if attributeId == self._lastServiceAttributeId:
    self.emit('servicesSet', self._setServicesError)
blenoBindings.on('kCBMsgId18', _temp16)
def _temp17(args, *varargs):
  deviceUUID = arrayToHex(args.kCBMsgArgDeviceUUID)
  mtu = args.kCBMsgArgATTMTU

  self._deviceUUID = buffer_from_hex(deviceUUID)
  self._deviceUUID.isUuid = True
  def _temp25(error, address, *varargs):
    self.emit('accept', address)
    self.emit('mtuChange', mtu)
  uuidToAddress(deviceUUID, bind(self, _temp25))
blenoBindings.on('kCBMsgId53', _temp17)
def _temp18(args, *varargs):
  attributeId = args.kCBMsgArgAttributeID
  offset = args.kCBMsgArgOffset or 0
  transactionId = args.kCBMsgArgTransactionID
  def _temp26(attributeId, transactionId, *varargs):
    def _temp27(result, data, *varargs):
      self.sendCBMsg(13, DotDict([
        ('kCBMsgArgAttributeID', attributeId),
        ('kCBMsgArgData', data),
        ('kCBMsgArgResult', result),
        ('kCBMsgArgTransactionID', transactionId)
      ]))
    return bind(self, _temp27)
  callback = bind(self, _temp26)(attributeId, transactionId)

  self._attributes[attributeId].emit('readRequest', offset, callback)
blenoBindings.on('kCBMsgId19', _temp18)
def _temp19(args, *varargs):
  attWrites = args.kCBMsgArgATTWrites
  transactionId = args.kCBMsgArgTransactionID

  i = 0
  while True:
    if not (i < len(attWrites)):
      break
    attWrite = attWrites[i]

    attributeId = attWrite.kCBMsgArgAttributeID
    data = attWrite.kCBMsgArgData
    ignoreResponse = True if attWrite.kCBMsgArgIgnoreResponse else False
    offset = args.kCBMsgArgOffset or 0
    def _temp28(attributeId, transactionId, ignoreResponse, *varargs):
      def _temp29(result, *varargs):
        if not ignoreResponse:
          self.sendCBMsg(13, DotDict([
            ('kCBMsgArgAttributeID', attributeId),
            ('kCBMsgArgData', None),
            ('kCBMsgArgResult', result),
            ('kCBMsgArgTransactionID', transactionId)
          ]))
      return bind(self, _temp29)
    callback = bind(self, _temp28)(attributeId, transactionId, ignoreResponse)

    self._attributes[attributeId].emit('writeRequest', data, offset, ignoreResponse, callback)
    i += 1
blenoBindings.on('kCBMsgId20', _temp19)
def _temp20(args, *varargs):
  attributeId = args.kCBMsgArgAttributeID
  maxValueSize = 20
  def _temp30(attributeId, *varargs):
    def _temp31(data, *varargs):
      self.sendCBMsg(15, DotDict([
        ('kCBMsgArgAttributeID', attributeId),
        ('kCBMsgArgData', data),
        ('kCBMsgArgUUIDs', GrowingList([]))
      ]))
    return bind(self, _temp31)
  callback = bind(self, _temp30)(attributeId)

  self._attributes[attributeId].emit('subscribe', maxValueSize, callback)
blenoBindings.on('kCBMsgId21', _temp20)
def _temp21(args, *varargs):
  attributeId = args.kCBMsgArgAttributeID

  self._attributes[attributeId].emit('unsubscribe')
blenoBindings.on('kCBMsgId22', _temp21)
def _temp22(args, *varargs):
  attributeId = args.kCBMsgArgAttributeID
  attribute = self._attributes[attributeId]

  if indexOf(attribute.properties, 'notify') != -1:
    attribute.emit('notify')

  if indexOf(attribute.properties, 'indicate') != -1:
    attribute.emit('indicate')
blenoBindings.on('kCBMsgId23', _temp22)
def _temp23(args, *varargs):
  rssi = args.kCBMsgArgData

  self.emit('rssiUpdate', rssi)
blenoBindings.on('kCBMsgId55', _temp23)

module.exports = blenoBindings