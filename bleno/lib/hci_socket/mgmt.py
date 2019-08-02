import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:13 UTC
# source: /lib/hci-socket/mgmt.js
# sha256: f02f044c88daef5b7cb827bc017a3ab4513659004a4182ba88321dfef839e423

math = require(__file__, 'math')
module = exports(__name__)
debug = require(__file__, '_debug')('mgmt')

events = require(__file__, '_events')
util = require(__file__, '_util')

BluetoothHciSocket = require(__file__, 'bluetooth_hci_socket')

LTK_INFO_SIZE = 36

MGMT_OP_LOAD_LONG_TERM_KEYS = 0x0013

class Mgmt():
  def __init__(self, *varargs):
    self._socket = BluetoothHciSocket()
    self._ltkInfos = GrowingList([])

    self._socket.on('data', bind(self, self.onSocketData))
    self._socket.on('error', bind(self, self.onSocketError))

    self._socket.bindControl()
    self._socket.start()

  def onSocketData(self, data, *varargs):
    debug('on data ->' + str(arrayToHex(data)))

  def onSocketError(self, error, *varargs):
    debug('on error ->' + str(error.message))

  def addLongTermKey(self, address, addressType, authenticated, master, ediv, rand, key, *varargs):
    ltkInfo = buffer(LTK_INFO_SIZE)

    address.copy(ltkInfo, 0)
    ltkInfo.writeUInt8(addressType.readUInt8(0) + 1, 6) # BDADDR_LE_PUBLIC = 0x01, BDADDR_LE_RANDOM 0x02, so add one

    ltkInfo.writeUInt8(authenticated, 7)
    ltkInfo.writeUInt8(master, 8)
    ltkInfo.writeUInt8(len(key), 9)

    ediv.copy(ltkInfo, 10)
    rand.copy(ltkInfo, 12)
    key.copy(ltkInfo, 20)

    self._ltkInfos.append(ltkInfo)

    self.loadLongTermKeys()

  def clearLongTermKeys(self, *varargs):
    self._ltkInfos = GrowingList([])

    self.loadLongTermKeys()

  def loadLongTermKeys(self, *varargs):
    numLongTermKeys = len(self._ltkInfos)
    op = buffer(2 + numLongTermKeys * LTK_INFO_SIZE)

    op.writeUInt16LE(numLongTermKeys, 0)

    i = 0
    while True:
      if not (i < numLongTermKeys):
        break
      self._ltkInfos[i].copy(op, 2 + i * LTK_INFO_SIZE)
      i += 1

    self.write(MGMT_OP_LOAD_LONG_TERM_KEYS, 0, op)

  def write(self, opcode, index, data=None, *varargs):
    length = 0

    if data:
      length = len(data)

    pkt = buffer(6 + length)

    pkt.writeUInt16LE(opcode, 0)
    pkt.writeUInt16LE(index, 2)
    pkt.writeUInt16LE(length, 4)

    if length:
      data.copy(pkt, 6)

    debug('writing -> ' + str(arrayToHex(pkt)))
    self._socket.write(pkt)

module.exports = Mgmt()