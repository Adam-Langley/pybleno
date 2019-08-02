import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:11 UTC
# source: /lib/mac/bindings.js
# sha256: 5fd221dcecc14e5f4fb2d2cb7e6ec9b11ccd44a2acbad845465382c6b5d8e5f4

math = require(__file__, 'math')
module = exports(__name__)
os = require(__file__, '_os')
osRelease = parseFloat(os.release())

if osRelease < 17:
  module.exports = require(__file__, './yosemite')
else:
  module.exports = require(__file__, './highsierra')