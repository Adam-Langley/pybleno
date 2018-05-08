from . import UuidUtil
import array

# function Descriptor(options) {
#   this.uuid = UuidUtil.removeDashes(options.uuid);
#   this.value = options.value || new Buffer(0);
# }

class Descriptor:
    def __init__(self, uuid=None, value=None):
        self.uuid = uuid
        if isinstance(value, basestring):
            self.value = array.array('B', [ord(c) for c in value])
        else:
            self.value = value
