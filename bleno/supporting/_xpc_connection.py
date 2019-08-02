from ._jshelpers import *

sys = require(__file__, 'sys')
module = sys.modules[__name__]

class XpcConnection():
    def __init__(self, target):
        pass
        
    def on(self, name, handler):
        pass

module.exports = XpcConnection