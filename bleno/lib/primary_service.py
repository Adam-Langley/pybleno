import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:11 UTC
# source: /lib/primary-service.js
# sha256: d127aedb01ebe4e9d86ac1e7a3e784d2a0e6227eee1a699a7d60482540a8c20c

require(__file__, 'json')
math = require(__file__, 'math')
module = exports(__name__)
events = require(__file__, '_events')
util = require(__file__, '_util')

debug = require(__file__, '_debug')('primary-service')

UuidUtil = require(__file__, './uuid_util')

class PrimaryService(events.EventEmitter):
  def __init__(self, options, *varargs):
    options = ensureIsDotDict(options)
    events.EventEmitter.__init__(self)
    self.uuid = UuidUtil.removeDashes(options.uuid)
    self.characteristics = options.characteristics or GrowingList([])

  def toString(self, *varargs):
    return json.dumps(DotDict([
      ('uuid', self.uuid),
      ('characteristics', self.characteristics)
    ]), indent = 4)

module.exports = PrimaryService