from .BluetoothHCI import *
from .Io import *

MGMT_OP_LOAD_LONG_TERM_KEYS = 0x0013

LTK_INFO_SIZE = 36

HCI_DEV_NONE = 0xffff
HCI_CHANNEL_RAW = 0
HCI_CHANNEL_UASER = 1
HCI_CHANNEL_CONTROL = 3

class Mgmt:
    def __init__(self):
        self._ltkInfos = []

        self._socket = BluetoothHCISocketProvider(HCI_DEV_NONE)     # device_id = 0
        self._socket.on_data(self.onSocketData)

        self._socket.open(HCI_CHANNEL_CONTROL)

    def onSocketData(self, data):
        print('MGMT READING: ', bytes(data).hex())

    def onSocketError(self, error):
        if error.message == 'Operation not permitted':
            self.emit('stateChange', ['unauthorized'])
        elif error.message == 'Network is down':
            pass  # no-op

    def addLongTermKey(self, address, addressType, authenticated, master, ediv, rand, key):
        ltkInfo = array.array('B', [0]*LTK_INFO_SIZE)

        address.reverse()
        copy(address,ltkInfo, 0)

        writeUInt8(ltkInfo, readUInt8(addressType,0) + 1, 6);
        writeUInt8(ltkInfo, authenticated, 7)
        writeUInt8(ltkInfo, master, 8)
        writeUInt8(ltkInfo, len(key), 9)

        copy(ediv, ltkInfo, 10)
        copy(rand, ltkInfo, 12)
        copy(key, ltkInfo, 20)

        self._ltkInfos.append(ltkInfo)
        self.loadLongTermKeys()

    def clearLongTermKeys(self):
        self._ltkInfos = []
        self.loadLongTermKeys()

    def loadLongTermKeys(self):
        numLongTermKeys = len(self._ltkInfos)
        op = array.array('B', [0] * (2 + numLongTermKeys * LTK_INFO_SIZE))

        print('LTK_INFO_SIZE: ', LTK_INFO_SIZE)
        print('numLongTermKeys: ', numLongTermKeys)

        writeUInt16LE(op, numLongTermKeys, 0);

        for i in range(numLongTermKeys):
            copy(self._ltkInfos[i], op, 2 + i * LTK_INFO_SIZE)

        self.write(MGMT_OP_LOAD_LONG_TERM_KEYS, 0, op)

    def write(self, opcode, index, data):
        length = 0

        if data:
            length = len(data)

        pkt = array.array('B', [0]*(6 + length))
        writeUInt16LE(pkt, opcode, 0)
        writeUInt16LE(pkt, index, 2)
        writeUInt16LE(pkt, length, 4)

        if length:
            copy(data, pkt, 6)

        self._socket.write_buffer(pkt)
