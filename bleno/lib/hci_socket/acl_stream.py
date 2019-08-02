import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:13 UTC
# source: /lib/hci-socket/acl-stream.js
# sha256: 4ce4bfb576fa0e6ea29f7f02ca556babf04146d5f0a2efa182bfd0e0b21539bf

math = require(__file__, 'math')
module = exports(__name__)
debug = require(__file__, '_debug')('acl-att-stream')

events = require(__file__, '_events')
util = require(__file__, '_util')

crypto = require(__file__, './crypto')
Smp = require(__file__, './smp')

class AclStream(events.EventEmitter):
  def __init__(self, hci, handle, localAddressType, localAddress, remoteAddressType, remoteAddress, *varargs):
    events.EventEmitter.__init__(self)
    self._hci = hci
    self._handle = handle
    self.encypted = False

    self._smp = Smp(self, localAddressType, localAddress, remoteAddressType, remoteAddress)

  def write(self, cid, data, *varargs):
    self._hci.queueAclDataPkt(self._handle, cid, data)

  def push(self, cid, data=None, *varargs):
    if data:
      self.emit('data', cid, data)
    else:
      self.emit('end')

  def pushEncrypt(self, encrypt, *varargs):
    self.encrypted = True if encrypt else False

    self.emit('encryptChange', self.encrypted)

  def pushLtkNegReply(self, *varargs):
    self.emit('ltkNegReply')

module.exports = AclStream