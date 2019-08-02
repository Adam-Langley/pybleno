import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:13 UTC
# source: /lib/hci-socket/smp.js
# sha256: 5379789e2baca302275c1bdedf46d10c2de7566769e3bd73804d0154db87b66a

math = require(__file__, 'math')
module = exports(__name__)
debug = require(__file__, '_debug')('smp')

events = require(__file__, '_events')
util = require(__file__, '_util')

crypto = require(__file__, './crypto')
mgmt = require(__file__, './mgmt')

SMP_CID = 0x0006

SMP_PAIRING_REQUEST = 0x01
SMP_PAIRING_RESPONSE = 0x02
SMP_PAIRING_CONFIRM = 0x03
SMP_PAIRING_RANDOM = 0x04
SMP_PAIRING_FAILED = 0x05
SMP_ENCRYPT_INFO = 0x06
SMP_MASTER_IDENT = 0x07

SMP_UNSPECIFIED = 0x08

class Smp(events.EventEmitter):
  def __init__(self, aclStream, localAddressType, localAddress, remoteAddressType, remoteAddress, *varargs):
    events.EventEmitter.__init__(self)
    self._aclStream = aclStream

    self._iat = buffer(GrowingList([0x01 if (remoteAddressType == 'random') else 0x00]))
    self._ia = buffer_from_hex(''.join(reverseAndReturn(remoteAddress.split(':'))))
    self._rat = buffer(GrowingList([0x01 if (localAddressType == 'random') else 0x00]))
    self._ra = buffer_from_hex(''.join(reverseAndReturn(localAddress.split(':'))))

    self._stk = None
    self._random = None
    self._diversifier = None

    self.onAclStreamDataBinded = bind(self, self.onAclStreamData)
    self.onAclStreamEncryptChangeBinded = bind(self, self.onAclStreamEncryptChange)
    self.onAclStreamLtkNegReplyBinded = bind(self, self.onAclStreamLtkNegReply)
    self.onAclStreamEndBinded = bind(self, self.onAclStreamEnd)

    self._aclStream.on('data', self.onAclStreamDataBinded)
    self._aclStream.on('encryptChange', self.onAclStreamEncryptChangeBinded)
    self._aclStream.on('ltkNegReply', self.onAclStreamLtkNegReplyBinded)
    self._aclStream.on('end', self.onAclStreamEndBinded)

  def onAclStreamData(self, cid, data, *varargs):
    if cid != SMP_CID:
      return

    code = data.readUInt8(0)

    if SMP_PAIRING_REQUEST == code:
      self.handlePairingRequest(data)
    elif SMP_PAIRING_CONFIRM == code:
      self.handlePairingConfirm(data)
    elif SMP_PAIRING_RANDOM == code:
      self.handlePairingRandom(data)
    elif SMP_PAIRING_FAILED == code:
      self.handlePairingFailed(data)

  def onAclStreamEncryptChange(self, encrypted=None, *varargs):
    if encrypted:
      if self._stk and self._diversifier and self._random:
        self.write(concat_lists(GrowingList([buffer(
          GrowingList([SMP_ENCRYPT_INFO])), 
          self._stk
        ])))

        self.write(concat_lists(GrowingList([buffer(
          GrowingList([SMP_MASTER_IDENT])), 
          self._diversifier, 
          self._random
        ])))

  def onAclStreamLtkNegReply(self, *varargs):
    self.write(buffer(GrowingList([
      SMP_PAIRING_FAILED, 
      SMP_UNSPECIFIED
    ])))

    self.emit('fail')

  def onAclStreamEnd(self, *varargs):
    self._aclStream.removeListener('data', self.onAclStreamDataBinded)
    self._aclStream.removeListener('encryptChange', self.onAclStreamEncryptChangeBinded)
    self._aclStream.removeListener('ltkNegReply', self.onAclStreamLtkNegReplyBinded)
    self._aclStream.removeListener('end', self.onAclStreamEndBinded)

  def handlePairingRequest(self, data, *varargs):
    self._preq = data

    self._pres = buffer(GrowingList([
      SMP_PAIRING_RESPONSE, 
      0x03,  # IO capability: NoInputNoOutput
      0x00,  # OOB data: Authentication data not present
      0x01,  # Authentication requirement: Bonding - No MITM
      0x10,  # Max encryption key size
      0x00,  # Initiator key distribution: <none>
      0x01 # Responder key distribution: EncKey
    ]))

    self.write(self._pres)

  def handlePairingConfirm(self, data, *varargs):
    self._pcnf = data

    self._tk = buffer_from_hex('00000000000000000000000000000000')
    self._r = crypto.r()

    self.write(concat_lists(GrowingList([buffer(
      GrowingList([SMP_PAIRING_CONFIRM])), 
      crypto.c1(self._tk, self._r, self._pres, self._preq, self._iat, self._ia, self._rat, self._ra)
    ])))

  def handlePairingRandom(self, data, *varargs):
    r = data.slice(1)

    pcnf = concat_lists(GrowingList([buffer(
      GrowingList([SMP_PAIRING_CONFIRM])), 
      crypto.c1(self._tk, r, self._pres, self._preq, self._iat, self._ia, self._rat, self._ra)
    ]))

    if arrayToHex(self._pcnf) == arrayToHex(pcnf):
      self._diversifier = buffer_from_hex('0000')
      self._random = buffer_from_hex('0000000000000000')
      self._stk = crypto.s1(self._tk, self._r, r)

      mgmt.addLongTermKey(self._ia, self._iat, 0, 0, self._diversifier, self._random, self._stk)

      self.write(concat_lists(GrowingList([buffer(
        GrowingList([SMP_PAIRING_RANDOM])), 
        self._r
      ])))
    else:
      self.write(buffer(GrowingList([
        SMP_PAIRING_FAILED, 
        SMP_PAIRING_CONFIRM
      ])))

      self.emit('fail')

  def handlePairingFailed(self, data, *varargs):
    self.emit('fail')

  def write(self, data, *varargs):
    self._aclStream.write(SMP_CID, data)

module.exports = Smp