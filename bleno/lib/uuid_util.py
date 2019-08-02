import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:11 UTC
# source: /lib/uuid-util.js
# sha256: 338e689252b7c93156d78db3a529031b39a8f62b5cc3fd70d5ee95f3b8051a5f

math = require(__file__, 'math')
module = exports(__name__)
def _temp(uuid, *varargs):
  if uuid:
    uuid = re.sub('-', '', uuid)

  return uuid
module.exports.removeDashes = _temp