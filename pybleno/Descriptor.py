import UuidUtil

# function Descriptor(options) {
#   this.uuid = UuidUtil.removeDashes(options.uuid);
#   this.value = options.value || new Buffer(0);
# }

class Descriptor:
    def __init__(self, uuid=None, value=None):
        self.uuid = uuid
        self.value = value
#   return JSON.stringify({
#     uuid: this.uuid,
#     value: Buffer.isBuffer(this.value) ? this.value.toString('hex') : this.value
#   });
# };

# module.exports = Descriptor;
