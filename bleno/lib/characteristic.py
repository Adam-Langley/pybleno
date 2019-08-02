import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:11 UTC
# source: /lib/characteristic.js
# sha256: 97844279bf7d0e7ebc3c6c5d47c12aaff329a98fa0e2797c4104081bad6246ac

require(__file__, 'json')
math = require(__file__, 'math')
module = exports(__name__)
events = require(__file__, '_events')
util = require(__file__, '_util')

debug = require(__file__, '_debug')('characteristic')

UuidUtil = require(__file__, './uuid_util')

class Characteristic(events.EventEmitter):
  def __init__(self, options, *varargs):
    options = ensureIsDotDict(options)
    events.EventEmitter.__init__(self)
    self.uuid = UuidUtil.removeDashes(options.uuid)
    self.properties = options.properties or GrowingList([])
    self.secure = options.secure or GrowingList([])
    self.value = options.value or None
    self.descriptors = options.descriptors or GrowingList([])

    if self.value and (len(self.properties) != 1 or self.properties[0] != 'read'):
      raise Error('Characteristics with value can be read only!')

    if options.onReadRequest:
      self.onReadRequest = options.onReadRequest

    if options.onWriteRequest:
      self.onWriteRequest = options.onWriteRequest

    if options.onSubscribe:
      self.onSubscribe = options.onSubscribe

    if options.onUnsubscribe:
      self.onUnsubscribe = options.onUnsubscribe

    if options.onNotify:
      self.onNotify = options.onNotify

    if options.onIndicate:
      self.onIndicate = options.onIndicate

    self.on('readRequest', bind(self, self.onReadRequest))
    self.on('writeRequest', bind(self, self.onWriteRequest))
    self.on('subscribe', bind(self, self.onSubscribe))
    self.on('unsubscribe', bind(self, self.onUnsubscribe))
    self.on('notify', bind(self, self.onNotify))
    self.on('indicate', bind(self, self.onIndicate))

  def toString(self, *varargs):
    return json.dumps(DotDict([
      ('uuid', self.uuid),
      ('properties', self.properties),
      ('secure', self.secure),
      ('value', self.value),
      ('descriptors', self.descriptors)
    ]), indent = 4)

  def onReadRequest(self, offset, callback, *varargs):
    callback(self.RESULT_UNLIKELY_ERROR, None)

  def onWriteRequest(self, data, offset, withoutResponse, callback, *varargs):
    callback(self.RESULT_UNLIKELY_ERROR)

  def onSubscribe(self, maxValueSize, updateValueCallback, *varargs):
    self.maxValueSize = maxValueSize
    self.updateValueCallback = updateValueCallback

  def onUnsubscribe(self, *varargs):
    self.maxValueSize = None
    self.updateValueCallback = None

  def onNotify(self, *varargs):
    pass

  def onIndicate(self, *varargs):
    pass

Characteristic.RESULT_SUCCESS = Characteristic.RESULT_SUCCESS = 0x00
Characteristic.RESULT_INVALID_OFFSET = Characteristic.RESULT_INVALID_OFFSET = 0x07
Characteristic.RESULT_ATTR_NOT_LONG = Characteristic.RESULT_ATTR_NOT_LONG = 0x0b
Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH = Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH = 0x0d
Characteristic.RESULT_UNLIKELY_ERROR = Characteristic.RESULT_UNLIKELY_ERROR = 0x0e

module.exports = Characteristic