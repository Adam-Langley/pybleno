import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:14 UTC
# source: /lib/hci-socket/hci.js
# sha256: 6ffece299b848345c8bea8ae7d87b99ff4c0c3ac7e4dfd371cf294e4eaa7bdcc

math = require(__file__, 'math')
module = exports(__name__)
debug = require(__file__, '_debug')('hci')

events = require(__file__, '_events')
util = require(__file__, '_util')

BluetoothHciSocket = require(__file__, 'bluetooth_hci_socket')

HCI_COMMAND_PKT = 0x01
HCI_ACLDATA_PKT = 0x02
HCI_EVENT_PKT = 0x04

ACL_START_NO_FLUSH = 0x00
ACL_CONT = 0x01
ACL_START = 0x02

EVT_DISCONN_COMPLETE = 0x05
EVT_ENCRYPT_CHANGE = 0x08
EVT_CMD_COMPLETE = 0x0e
EVT_CMD_STATUS = 0x0f
EVT_NUMBER_OF_COMPLETED_PACKETS = 0x13
EVT_LE_META_EVENT = 0x3e

EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_CONN_UPDATE_COMPLETE = 0x03

OGF_LINK_CTL = 0x01
OCF_DISCONNECT = 0x0006

OGF_HOST_CTL = 0x03
OCF_SET_EVENT_MASK = 0x0001
OCF_RESET = 0x0003
OCF_READ_LE_HOST_SUPPORTED = 0x006c
OCF_WRITE_LE_HOST_SUPPORTED = 0x006d

OGF_INFO_PARAM = 0x04
OCF_READ_LOCAL_VERSION = 0x0001
OCF_READ_BUFFER_SIZE = 0x0005
OCF_READ_BD_ADDR = 0x0009

OGF_STATUS_PARAM = 0x05
OCF_READ_RSSI = 0x0005

OGF_LE_CTL = 0x08
OCF_LE_SET_EVENT_MASK = 0x0001
OCF_LE_READ_BUFFER_SIZE = 0x0002
OCF_LE_SET_ADVERTISING_PARAMETERS = 0x0006
OCF_LE_SET_ADVERTISING_DATA = 0x0008
OCF_LE_SET_SCAN_RESPONSE_DATA = 0x0009
OCF_LE_SET_ADVERTISE_ENABLE = 0x000a
OCF_LE_LTK_NEG_REPLY = 0x001B

DISCONNECT_CMD = OCF_DISCONNECT | OGF_LINK_CTL << 10

SET_EVENT_MASK_CMD = OCF_SET_EVENT_MASK | OGF_HOST_CTL << 10
RESET_CMD = OCF_RESET | OGF_HOST_CTL << 10
READ_LE_HOST_SUPPORTED_CMD = OCF_READ_LE_HOST_SUPPORTED | OGF_HOST_CTL << 10
WRITE_LE_HOST_SUPPORTED_CMD = OCF_WRITE_LE_HOST_SUPPORTED | OGF_HOST_CTL << 10

READ_LOCAL_VERSION_CMD = OCF_READ_LOCAL_VERSION | (OGF_INFO_PARAM << 10)
READ_BUFFER_SIZE_CMD = OCF_READ_BUFFER_SIZE | (OGF_INFO_PARAM << 10)
READ_BD_ADDR_CMD = OCF_READ_BD_ADDR | (OGF_INFO_PARAM << 10)

READ_RSSI_CMD = OCF_READ_RSSI | OGF_STATUS_PARAM << 10

LE_SET_EVENT_MASK_CMD = OCF_LE_SET_EVENT_MASK | OGF_LE_CTL << 10
LE_READ_BUFFER_SIZE_CMD = OCF_LE_READ_BUFFER_SIZE | OGF_LE_CTL << 10
LE_SET_ADVERTISING_PARAMETERS_CMD = OCF_LE_SET_ADVERTISING_PARAMETERS | OGF_LE_CTL << 10
LE_SET_ADVERTISING_DATA_CMD = OCF_LE_SET_ADVERTISING_DATA | OGF_LE_CTL << 10
LE_SET_SCAN_RESPONSE_DATA_CMD = OCF_LE_SET_SCAN_RESPONSE_DATA | OGF_LE_CTL << 10
LE_SET_ADVERTISE_ENABLE_CMD = OCF_LE_SET_ADVERTISE_ENABLE | OGF_LE_CTL << 10
LE_LTK_NEG_REPLY_CMD = OCF_LE_LTK_NEG_REPLY | OGF_LE_CTL << 10

HCI_OE_USER_ENDED_CONNECTION = 0x13

STATUS_MAPPER = require(__file__, './hci_status')

class Hci(events.EventEmitter):
  def __init__(self, *varargs):
    events.EventEmitter.__init__(self)
    self._socket = BluetoothHciSocket()
    self._isDevUp = None
    self._state = None
    self._deviceId = None
    # le-u min payload size + l2cap header size
    # see Bluetooth spec 4.2 [Vol 3, Part A, Chapter 4]
    self._aclMtu = 23 + 4
    self._aclMaxInProgress = 1

    self.resetBuffers()

    self.on('stateChange', bind(self, self.onStateChange))

  def init(self, *varargs):
    self._socket.on('data', bind(self, self.onSocketData))
    self._socket.on('error', bind(self, self.onSocketError))

    deviceId = parseInt(process.env.BLENO_HCI_DEVICE_ID) if process.env.BLENO_HCI_DEVICE_ID else None


    if process.env.HCI_CHANNEL_USER:
      self._deviceId = self._socket.bindUser(deviceId)

      self._socket.start()

      self.reset()
    else:
      self._deviceId = self._socket.bindRaw(deviceId)
      self._socket.start()

      self.pollIsDevUp()

  def resetBuffers(self, *varargs):
    self._handleAclsInProgress = DotDict([])
    self._handleBuffers = DotDict([])
    self._aclOutQueue = GrowingList([])

  def pollIsDevUp(self, *varargs):
    isDevUp = self._socket.isDevUp()

    if self._isDevUp != isDevUp:
      if isDevUp:
        self.setSocketFilter()
        self.initDev()
      else:
        self.emit('stateChange', 'poweredOff')

      self._isDevUp = isDevUp

    setTimeout(bind(self, self.pollIsDevUp), 1000)

  def initDev(self, *varargs):
    self.resetBuffers()
    self.setEventMask()
    self.setLeEventMask()
    self.readLocalVersion()
    self.writeLeHostSupported()
    self.readLeHostSupported()
    self.readBdAddr()
    self.leReadBufferSize()

  def setSocketFilter(self, *varargs):
    filter = buffer(14)
    typeMask = (1 << HCI_EVENT_PKT) | (1 << HCI_ACLDATA_PKT)
    eventMask1 = (1 << EVT_DISCONN_COMPLETE) | (1 << EVT_ENCRYPT_CHANGE) | (1 << EVT_CMD_COMPLETE) | (1 << EVT_CMD_STATUS) | (1 << EVT_NUMBER_OF_COMPLETED_PACKETS)
    eventMask2 = (1 << (EVT_LE_META_EVENT - 32))
    opcode = 0

    filter.writeUInt32LE(typeMask, 0)
    filter.writeUInt32LE(eventMask1, 4)
    filter.writeUInt32LE(eventMask2, 8)
    filter.writeUInt16LE(opcode, 12)

    debug('setting filter to: ' + str(arrayToHex(filter)))
    self._socket.setFilter(filter)

  def setEventMask(self, *varargs):
    cmd = buffer(12)
    eventMask = buffer_from_hex('fffffbff07f8bf3d')

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(SET_EVENT_MASK_CMD, 1)

    # length
    cmd.writeUInt8(len(eventMask), 3)

    eventMask.copy(cmd, 4)

    debug('set event mask - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def reset(self, *varargs):
    cmd = buffer(4)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(OCF_RESET | OGF_HOST_CTL << 10, 1)

    # length
    cmd.writeUInt8(0x00, 3)

    debug('reset - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def readLeHostSupported(self, *varargs):
    cmd = buffer(4)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(READ_LE_HOST_SUPPORTED_CMD, 1)

    # length
    cmd.writeUInt8(0x00, 3)

    debug('read LE host supported - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def writeLeHostSupported(self, *varargs):
    cmd = buffer(6)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(WRITE_LE_HOST_SUPPORTED_CMD, 1)

    # length
    cmd.writeUInt8(0x02, 3)

    # data
    cmd.writeUInt8(0x01, 4) # le
    cmd.writeUInt8(0x00, 5) # simul

    debug('write LE host supported - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def readLocalVersion(self, *varargs):
    cmd = buffer(4)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(READ_LOCAL_VERSION_CMD, 1)

    # length
    cmd.writeUInt8(0x0, 3)

    debug('read local version - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def readBdAddr(self, *varargs):
    cmd = buffer(4)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(READ_BD_ADDR_CMD, 1)

    # length
    cmd.writeUInt8(0x0, 3)

    debug('read bd addr - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def setLeEventMask(self, *varargs):
    cmd = buffer(12)
    leEventMask = buffer_from_hex('1f00000000000000')

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(LE_SET_EVENT_MASK_CMD, 1)

    # length
    cmd.writeUInt8(len(leEventMask), 3)

    leEventMask.copy(cmd, 4)

    debug('set le event mask - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def setAdvertisingParameters(self, *varargs):
    cmd = buffer(19)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(LE_SET_ADVERTISING_PARAMETERS_CMD, 1)

    # length
    cmd.writeUInt8(15, 3)

    advertisementInterval = math.floor((parseFloat(process.env.BLENO_ADVERTISING_INTERVAL) if process.env.BLENO_ADVERTISING_INTERVAL else 100) * 1.6)

    # data
    cmd.writeUInt16LE(advertisementInterval, 4) # min interval
    cmd.writeUInt16LE(advertisementInterval, 6) # max interval
    cmd.writeUInt8(0x00, 8) # adv type
    cmd.writeUInt8(0x00, 9) # own addr typ
    cmd.writeUInt8(0x00, 10) # direct addr type
    buffer_from_hex('000000000000').copy(cmd, 11) # direct addr
    cmd.writeUInt8(0x07, 17)
    cmd.writeUInt8(0x00, 18)

    debug('set advertisement parameters - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def setAdvertisingData(self, data, *varargs):
    cmd = buffer(36)

    cmd.fill(0x00)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(LE_SET_ADVERTISING_DATA_CMD, 1)

    # length
    cmd.writeUInt8(32, 3)

    # data
    cmd.writeUInt8(len(data), 4)
    data.copy(cmd, 5)

    debug('set advertisement data - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def setScanResponseData(self, data, *varargs):
    cmd = buffer(36)

    cmd.fill(0x00)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(LE_SET_SCAN_RESPONSE_DATA_CMD, 1)

    # length
    cmd.writeUInt8(32, 3)

    # data
    cmd.writeUInt8(len(data), 4)
    data.copy(cmd, 5)

    debug('set scan response data - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def setAdvertiseEnable(self, enabled, *varargs):
    cmd = buffer(5)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(LE_SET_ADVERTISE_ENABLE_CMD, 1)

    # length
    cmd.writeUInt8(0x01, 3)

    # data
    cmd.writeUInt8(0x01 if enabled else 0x00, 4) # enable: 0 -> disabled, 1 -> enabled

    debug('set advertise enable - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def disconnect(self, handle, reason=None, *varargs):
    cmd = buffer(7)

    reason = reason or HCI_OE_USER_ENDED_CONNECTION

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(DISCONNECT_CMD, 1)

    # length
    cmd.writeUInt8(0x03, 3)

    # data
    cmd.writeUInt16LE(handle, 4) # handle
    cmd.writeUInt8(reason, 6) # reason

    debug('disconnect - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def readRssi(self, handle, *varargs):
    cmd = buffer(6)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(READ_RSSI_CMD, 1)

    # length
    cmd.writeUInt8(0x02, 3)

    # data
    cmd.writeUInt16LE(handle, 4) # handle

    debug('read rssi - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def leReadBufferSize(self, *varargs):
    cmd = buffer(4)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(LE_READ_BUFFER_SIZE_CMD, 1)

    # length
    cmd.writeUInt8(0x0, 3)

    debug('le read buffer size - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def readBufferSize(self, *varargs):
    cmd = buffer(4)

    # header
    cmd.writeUInt8(HCI_COMMAND_PKT, 0)
    cmd.writeUInt16LE(READ_BUFFER_SIZE_CMD, 1)

    # length
    cmd.writeUInt8(0x0, 3)

    debug('read buffer size - writing: ' + str(arrayToHex(cmd)))
    self._socket.write(cmd)

  def queueAclDataPkt(self, handle, cid, data, *varargs):
    hf = handle | ACL_START_NO_FLUSH << 12
    # l2cap pdu may be fragmented on hci level
    l2capPdu = buffer(4 + len(data))
    l2capPdu.writeUInt16LE(len(data), 0)
    l2capPdu.writeUInt16LE(cid, 2)
    data.copy(l2capPdu, 4)
    fragId = 0

    while len(l2capPdu):
      frag = l2capPdu.slice(0, self._aclMtu)
      l2capPdu = l2capPdu.slice(len(frag))
      pkt = buffer(5 + len(frag))

      # hci header
      pkt.writeUInt8(HCI_ACLDATA_PKT, 0)
      pkt.writeUInt16LE(hf, 1)
      hf |= ACL_CONT << 12
      pkt.writeUInt16LE(len(frag), 3) # hci pdu length

      frag.copy(pkt, 5)

      self._aclOutQueue.append(DotDict([
        ('handle', handle),
        ('pkt', pkt),
        ('fragId', fragId)
      ]))
      fragId += 1

    self.pushAclOutQueue()

  def pushAclOutQueue(self, *varargs):
    inProgress = 0
    for handle in self._handleAclsInProgress or GrowingList([]):
      inProgress += self._handleAclsInProgress[handle]
    while inProgress < self._aclMaxInProgress and len(self._aclOutQueue):
      inProgress += 1
      self.writeOneAclDataPkt()

    if inProgress >= self._aclMaxInProgress and len(self._aclOutQueue):
      debug('acl out queue congested')
      debug('	in progress = ' + str(inProgress))
      debug('	waiting = ' + str(len(self._aclOutQueue)))

  def writeOneAclDataPkt(self, *varargs):
    pkt = self._aclOutQueue.shift()
    self._handleAclsInProgress[pkt.handle] += 1
    debug('write acl data pkt frag ' + str(pkt.fragId) + ' handle ' + str(pkt.handle) + ' - writing: ' + arrayToHex(pkt.pkt))
    self._socket.write(pkt.pkt)

  def onSocketData(self, data, *varargs):
    debug('onSocketData: ' + str(arrayToHex(data)))

    eventType = data.readUInt8(0)
    handle = None

    debug('	event type = ' + str(eventType))

    if HCI_EVENT_PKT == eventType:
      subEventType = data.readUInt8(1)

      debug('	sub event type = ' + str(subEventType))

      if subEventType == EVT_DISCONN_COMPLETE:
        handle = data.readUInt16LE(4)
        reason = data.readUInt8(6)

        debug('		handle = ' + str(handle))
        debug('		reason = ' + str(reason))

        # As per Bluetooth Core specs:
        # When the Host receives a Disconnection Complete, Disconnection Physical
        # Link Complete or Disconnection Logical Link Complete event, the Host shall
        # assume that all unacknowledged HCI Data Packets that have been sent to the
        # Controller for the returned Handle have been flushed, and that the
        # corresponding data buffers have been freed.
        del self._handleAclsInProgress[handle]
        aclOutQueue = GrowingList([])
        discarded = 0
        for i in self._aclOutQueue or GrowingList([]):
          if self._aclOutQueue[i].handle != handle:
            aclOutQueue.append(self._aclOutQueue[i])
          else:
            discarded += 1
        if discarded:
          debug('		acls discarded = ' + str(discarded))
        self._aclOutQueue = aclOutQueue
        self.pushAclOutQueue()
        self.emit('disconnComplete', handle, reason)
      elif subEventType == EVT_ENCRYPT_CHANGE:
        handle = data.readUInt16LE(4)
        encrypt = data.readUInt8(6)

        debug('		handle = ' + str(handle))
        debug('		encrypt = ' + str(encrypt))

        self.emit('encryptChange', handle, encrypt)
      elif subEventType == EVT_CMD_COMPLETE:
        ncmd = data.readUInt8(3)
        cmd = data.readUInt16LE(4)
        status = data.readUInt8(6)
        result = data.slice(7)

        debug('		ncmd = ' + str(ncmd))
        debug('		cmd = ' + str(cmd))
        debug('		status = ' + str(status))
        debug('		result = ' + str(arrayToHex(result)))

        self.processCmdCompleteEvent(cmd, status, result)
      elif subEventType == EVT_LE_META_EVENT:
        leMetaEventType = data.readUInt8(3)
        leMetaEventStatus = data.readUInt8(4)
        leMetaEventData = data.slice(5)

        debug('		LE meta event type = ' + str(leMetaEventType))
        debug('		LE meta event status = ' + str(leMetaEventStatus))
        debug('		LE meta event data = ' + str(arrayToHex(leMetaEventData)))

        self.processLeMetaEvent(leMetaEventType, leMetaEventStatus, leMetaEventData)
      elif subEventType == EVT_NUMBER_OF_COMPLETED_PACKETS:
        handles = data.readUInt8(3)
        i = 0
        while True:
          if not (i < handles):
            break
          handle = data.readUInt16LE(4 + i * 4)
          pkts = data.readUInt16LE(6 + i * 4)
          debug('	handle = ' + str(handle))
          debug('		completed = ' + str(pkts))
          if self._handleAclsInProgress[handle] == None:
            debug('		already closed')
          if pkts > self._handleAclsInProgress[handle]:
            # Linux kernel may send acl packets by itself, so be ready for underflow
            self._handleAclsInProgress[handle] = 0
          else:
            self._handleAclsInProgress[handle] -= pkts
          debug('		in progress = ' + str(self._handleAclsInProgress[handle]))
          i += 1
        self.pushAclOutQueue()
    elif HCI_ACLDATA_PKT == eventType:
      flags = data.readUInt16LE(1) >> 12
      handle = data.readUInt16LE(1) & 0x0fff

      if ACL_START == flags:
        cid = data.readUInt16LE(7)

        length = data.readUInt16LE(5)
        pktData = data.slice(9)

        debug('		cid = ' + str(cid))

        if length == len(pktData):
          debug('		handle = ' + str(handle))
          debug('		data = ' + str(arrayToHex(pktData)))

          self.emit('aclDataPkt', handle, cid, pktData)
        else:
          self._handleBuffers[handle] = DotDict([
            ('length', length),
            ('cid', cid),
            ('data', pktData)
          ])
      elif ACL_CONT == flags:
        if not self._handleBuffers[handle] or not self._handleBuffers[handle].data:
          return

        self._handleBuffers[handle].data = concat_lists(GrowingList([
          self._handleBuffers[handle].data, 
          data.slice(5)
        ]))

        if len(self._handleBuffers[handle].data) == len(self._handleBuffers[handle]):
          self.emit('aclDataPkt', handle, self._handleBuffers[handle].cid, self._handleBuffers[handle].data)

          del self._handleBuffers[handle]

  def onSocketError(self, error, *varargs):
    debug('onSocketError: ' + str(error.message))

    if error.message == 'Operation not permitted':
      self.emit('stateChange', 'unauthorized')
    elif error.message == 'Network is down':
      pass

  def processCmdCompleteEvent(self, cmd, status, result, *varargs):
    handle = None

    if cmd == RESET_CMD:
      self.initDev()
    elif cmd == READ_LE_HOST_SUPPORTED_CMD:
      if status == 0:
        le = result.readUInt8(0)
        simul = result.readUInt8(1)

        debug('			le = ' + str(le))
        debug('			simul = ' + str(simul))
    elif cmd == READ_LOCAL_VERSION_CMD:
      hciVer = result.readUInt8(0)
      hciRev = result.readUInt16LE(1)
      lmpVer = result.readInt8(3)
      manufacturer = result.readUInt16LE(4)
      lmpSubVer = result.readUInt16LE(6)

      if hciVer < 0x06:
        self.emit('stateChange', 'unsupported')
      elif self._state != 'poweredOn':
        self.setAdvertiseEnable(False)
        self.setAdvertisingParameters()

      self.emit('readLocalVersion', hciVer, hciRev, lmpVer, manufacturer, lmpSubVer)
    elif cmd == READ_BD_ADDR_CMD:
      self.addressType = 'public'
      self.address = ':'.join(reverseAndReturn(re.findall('.{1,2}', arrayToHex(result))))

      debug('address = ' + str(self.address))

      self.emit('addressChange', self.address)
    elif cmd == LE_SET_ADVERTISING_PARAMETERS_CMD:
      self.emit('stateChange', 'poweredOn')

      self.emit('leAdvertisingParametersSet', status)
    elif cmd == LE_SET_ADVERTISING_DATA_CMD:
      self.emit('leAdvertisingDataSet', status)
    elif cmd == LE_SET_SCAN_RESPONSE_DATA_CMD:
      self.emit('leScanResponseDataSet', status)
    elif cmd == LE_SET_ADVERTISE_ENABLE_CMD:
      self.emit('leAdvertiseEnableSet', status)
    elif cmd == READ_RSSI_CMD:
      handle = result.readUInt16LE(0)
      rssi = result.readInt8(2)

      debug('			handle = ' + str(handle))
      debug('			rssi = ' + str(rssi))

      self.emit('rssiRead', handle, rssi)
    elif cmd == LE_LTK_NEG_REPLY_CMD:
      handle = result.readUInt16LE(0)

      debug('			handle = ' + str(handle))
      self.emit('leLtkNegReply', handle)
    elif cmd == LE_READ_BUFFER_SIZE_CMD:
      if not status:
        self.processLeReadBufferSize(result)
    elif cmd == READ_BUFFER_SIZE_CMD:
      if not status:
        aclMtu = result.readUInt16LE(0)
        aclMaxInProgress = result.readUInt16LE(3)
        # sanity
        if aclMtu and aclMaxInProgress:
          debug('br/edr acl mtu = ' + str(aclMtu))
          debug('br/edr acl max pkts = ' + str(aclMaxInProgress))
          self._aclMtu = aclMtu
          self._aclMaxInProgress = aclMaxInProgress

  def processLeReadBufferSize(self, result, *varargs):
    aclMtu = result.readUInt16LE(0)
    aclMaxInProgress = result.readUInt8(2)
    if not aclMtu:
      # as per Bluetooth specs
      debug('falling back to br/edr buffer size')
      self.readBufferSize()
    else:
      debug('le acl mtu = ' + str(aclMtu))
      debug('le acl max in progress = ' + str(aclMaxInProgress))
      self._aclMtu = aclMtu
      self._aclMaxInProgress = aclMaxInProgress

  def processLeMetaEvent(self, eventType, status, data, *varargs):
    if eventType == EVT_LE_CONN_COMPLETE:
      self.processLeConnComplete(status, data)
    elif eventType == EVT_LE_CONN_UPDATE_COMPLETE:
      self.processLeConnUpdateComplete(status, data)

  def processLeConnComplete(self, status, data, *varargs):
    handle = data.readUInt16LE(0)
    role = data.readUInt8(2)
    addressType = 'random' if data.readUInt8(3) == 0x01 else 'public'
    address = ':'.join(reverseAndReturn(re.findall('.{1,2}', arrayToHex(data.slice(4, 10)))))
    interval = data.readUInt16LE(10) * 1.25
    latency = data.readUInt16LE(12) # TODO: multiplier?
    supervisionTimeout = data.readUInt16LE(14) * 10
    masterClockAccuracy = data.readUInt8(16) # TODO: multiplier?
    debug('			handle = ' + str(handle))
    debug('			role = ' + str(role))
    debug('			address type = ' + str(addressType))
    debug('			address = ' + str(address))
    debug('			interval = ' + str(interval))
    debug('			latency = ' + str(latency))
    debug('			supervision timeout = ' + str(supervisionTimeout))
    debug('			master clock accuracy = ' + str(masterClockAccuracy))

    self._handleAclsInProgress[handle] = 0

    self.emit('leConnComplete', status, handle, role, addressType, address, interval, latency, supervisionTimeout, masterClockAccuracy)

  def processLeConnUpdateComplete(self, status, data, *varargs):
    handle = data.readUInt16LE(0)
    interval = data.readUInt16LE(2) * 1.25
    latency = data.readUInt16LE(4) # TODO: multiplier?
    supervisionTimeout = data.readUInt16LE(6) * 10

    debug('			handle = ' + str(handle))
    debug('			interval = ' + str(interval))
    debug('			latency = ' + str(latency))
    debug('			supervision timeout = ' + str(supervisionTimeout))

    self.emit('leConnUpdateComplete', status, handle, interval, latency, supervisionTimeout)

  def onStateChange(self, state, *varargs):
    self._state = state

Hci.STATUS_MAPPER = STATUS_MAPPER

module.exports = Hci