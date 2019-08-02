import array
import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:11 UTC
# source: /lib/descriptor.js
# sha256: 507e63dfa78e158e3a0760d26924a98809337002d402c65ea87e32b423b80f7d

require(__file__, 'json')
math = require(__file__, 'math')
module = exports(__name__)
debug = require(__file__, '_debug')('descriptor')

UuidUtil = require(__file__, './uuid_util')

class Descriptor():
  def __init__(self, options, *varargs):
    options = ensureIsDotDict(options)
    self.uuid = UuidUtil.removeDashes(options.uuid)
    self.value = options.value or buffer(0)

  def toString(self, *varargs):
    return json.dumps(DotDict([
      ('uuid', self.uuid),
      ('value', arrayToHex(self.value) if isinstance(self.value, array.array) else self.value)
    ]), indent = 4)

module.exports = Descriptor