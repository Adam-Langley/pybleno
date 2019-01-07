from . import UuidUtil
import array
import traceback

# function Descriptor(options) {
#   this.uuid = UuidUtil.removeDashes(options.uuid);
#   this.value = options.value || new Buffer(0);
# }

class Descriptor:
    def __init__(self, options):
        self.uuid = options['uuid'] 
        if isinstance(options['value'], str):
            self.value = array.array('B', [ord(c) for c in options['value']])
        else:
            self.value = options['value']
