import threading
import math
import time
from . import Emit
from .BluetoothHCI import *
# from constants import *
from .constants2 import *
from os import popen
import codecs
from .Io import *
from .HciStatus import *


class Hci:
    STATUS_MAPPER = STATUS_MAPPER

    def __init__(self):
        self._events = {}

        self._socket = BluetoothHCI(auto_start=False)
        self._isDevUp = None
        self._state = None
        self._deviceId = None

        self._handleBuffers = {}

        self.on('stateChange', self.onStateChange)

    def init(self):

        self._socket.on_data(self.onSocketData)

        self._socket.on_started(self.on_socket_started)

        # self._socket_up_poll_thread = threading.Thread(target=self._socket_up_poller, name='HCISocketUpPoller')
        # self._socket_up_poll_thread.setDaemon(True)
        # self._socket_up_poll_thread.start()

        self._socket.start()

    #     self._socket_up_poll_thread = threading.Thread(target=self.io_thread, name='HCISocketUpPoller2')
    #     self._socket_up_poll_thread.setDaemon(True)
    #     self._socket_up_poll_thread.start()

    # def io_thread(self):
    #     while True:

    #         pass

    def setSocketFilter(self):
        typeMask = (1 << HCI_EVENT_PKT) | (1 << HCI_ACLDATA_PKT)
        eventMask1 = (1 << EVT_DISCONN_COMPLETE) | (1 << EVT_ENCRYPT_CHANGE) | (1 << EVT_CMD_COMPLETE) | (
                    1 << EVT_CMD_STATUS)
        eventMask2 = (1 << (EVT_LE_META_EVENT - 32))
        opcode = 0

        # debug('setting filter to: ' + filter.toString('hex'))
        filter = struct.pack("<LLLH", typeMask, eventMask1, eventMask2, opcode)
        self._socket.set_filter(filter)

    def setEventMask(self):
        # cmd = new Buffer(12)
        # eventMask = new Buffer('fffffbff07f8bf3d', 'hex')

        ## header
        # cmd.writeUInt8(HCI_COMMAND_PKT, 0)
        # cmd.writeUInt16LE(SET_EVENT_MASK_CMD, 1)

        ## length
        # cmd.writeUInt8(eventMask.length, 3)

        # eventMask.copy(cmd, 4)

        cmd = array.array('B', [0] * 12)
        struct.pack_into("<BHB", cmd, 0, HCI_COMMAND_PKT, SET_EVENT_MASK_CMD, 8)
        struct.pack_into(">Q", cmd, 4, 0xfffffbff07f8bf3d)
        # debug('set event mask - writing: ' + cmd.toString('hex'))
        self.write(cmd)

    def reset(self):
        cmd = array.array('B', [0] * 4)

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, OCF_RESET | OGF_HOST_CTL << 10, 1)

        # length
        writeUInt8(cmd, 0x00, 3)

        # debug('reset');
        self.write_buffer(cmd)

    def readLeHostSupported(self):
        cmd = array.array('B', [0] * 4)

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, READ_LE_HOST_SUPPORTED_CMD, 1)

        # length
        writeUInt8(cmd, 0x00, 3)
        # struct.pack_into("<BHB", cmd, 0, HCI_COMMAND_PKT, READ_LE_HOST_SUPPORTED_CMD, 0x00)

        # debug('read LE host supported - writing: ' + cmd.toString('hex'))
        self.write(cmd)

    def writeLeHostSupported(self):
        # cmd = new Buffer(6)
        cmd = array.array('B', [0] * 6)

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, WRITE_LE_HOST_SUPPORTED_CMD, 1)

        # length
        writeUInt8(cmd, 0x02, 3)

        # data
        writeUInt8(cmd, 0x01, 4)  # le
        writeUInt8(cmd, 0x00, 5)  # simul

        # struct.pack_into("<BHBBB", cmd, 0, HCI_COMMAND_PKT, WRITE_LE_HOST_SUPPORTED_CMD, 0x02, 0x01, 0x00)

        # debug('write LE host supported - writing: ' + cmd.toString('hex'))
        # print [hex(c) for c in cmd]
        self.write(cmd)

    def readLocalVersion(self):
        cmd = array.array('B', [0] * 4)

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, READ_LOCAL_VERSION_CMD, 1)

        # length
        writeUInt8(cmd, 0x0, 3)
        # struct.pack_into("<BHB", cmd, 0, HCI_COMMAND_PKT, READ_LOCAL_VERSION_CMD, 0)

        # debug('read local version - writing: ' + cmd.toString('hex'))
        self.write(cmd)

    def readBdAddr(self):
        cmd = array.array('B', [0] * 4)
        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, READ_BD_ADDR_CMD, 1)

        # length
        writeUInt8(cmd, 0x0, 3)
        # struct.pack_into("<BHB", cmd, 0, HCI_COMMAND_PKT, READ_BD_ADDR_CMD, 0x00)

        # debug('read bd addr - writing: ' + cmd.toString('hex'))
        self.write(cmd)

    def setLeEventMask(self):
        # #cmd = new Buffer(12)
        # cmd = array.array('B', [0] * 12)
        # #leEventMask = new Buffer('1f00000000000000', 'hex')
        # leEventMask = '1f00000000000000'

        # # # header
        # # cmd.writeUInt8(HCI_COMMAND_PKT, 0)
        # # cmd.writeUInt16LE(LE_SET_EVENT_MASK_CMD, 1)
        # struct.pack_into("<BH", cmd, 0, HCI_COMMAND_PKT, LE_SET_EVENT_MASK_CMD)

        # # # length
        # #cmd.writeUInt8(leEventMask.length, 3)
        # struct.pack_into("<B", cmd, 3, len(leEventMask) / 2)

        # struct.pack_into(">Q", cmd, 4, int(leEventMask, 16))
        # #leEventMask.copy(cmd, 4)

        # #debug('set le event mask - writing: ' + cmd.toString('hex'))
        # #print [hex(c) for c in cmd]
        # self.write(cmd)
        cmd = array.array('B', [0] * 12)
        leEventMask = array.array('B', bytearray.fromhex('1f00000000000000'))

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, LE_SET_EVENT_MASK_CMD, 1)

        # length
        writeUInt8(cmd, len(leEventMask), 3)

        copy(leEventMask, cmd, 4)

        # debug('set le event mask - writing: ' + cmd.toString('hex'));
        # console.log('set le event mask - writing: ' + cmd.toString('hex'));
        self.write(cmd)

    def setAdvertisingParameters(self):
        # cmd = new Buffer(19)
        cmd = array.array('B', [0] * 19)

        # # header
        # cmd.writeUInt8(HCI_COMMAND_PKT, 0)
        # cmd.writeUInt16LE(LE_SET_ADVERTISING_PARAMETERS_CMD, 1)

        # # length
        # cmd.writeUInt8(15, 3)

        # advertisementInterval = Math.floor((process.env.BLENO_ADVERTISING_INTERVAL ? parseFloat(process.env.BLENO_ADVERTISING_INTERVAL) : 100) * 1.6)
        advertisementInterval = math.floor(100 * 1.6)

        # # data
        # cmd.writeUInt16LE(advertisementInterval, 4); # min interval
        # cmd.writeUInt16LE(advertisementInterval, 6); # max interval
        # cmd.writeUInt8(0x00, 8); # adv type
        # cmd.writeUInt8(0x00, 9); # own addr typ
        # cmd.writeUInt8(0x00, 10); # direct addr type
        # (new Buffer('000000000000', 'hex')).copy(cmd, 11); # direct addr
        # cmd.writeUInt8(0x07, 17)
        # cmd.writeUInt8(0x00, 18)

        struct.pack_into("<BHBHHBBBIHBB", cmd, 0, HCI_COMMAND_PKT, LE_SET_ADVERTISING_PARAMETERS_CMD, 15,
                         advertisementInterval, advertisementInterval, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00)

        # debug('set advertisement parameters - writing: ' + cmd.toString('hex'))
        # print('set advertise parameters - writing: ' + `[hex(c) for c in cmd]`)
        self.write(cmd)

    def setAdvertisingData(self, data):
        cmd = array.array('B', [0] * 36)

        # cmd.fill(0x00)

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, LE_SET_ADVERTISING_DATA_CMD, 1)

        # length
        writeUInt8(cmd, 32, 3)

        # data
        writeUInt8(cmd, len(data), 4)
        copy(data, cmd, 5)

        # debug('set advertisement data - writing: ' + cmd.toString('hex'))
        self.write(cmd)

    def setScanResponseData(self, data):
        cmd = array.array('B', [0] * 36)
        #     cmd.fill(0x00)

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, LE_SET_SCAN_RESPONSE_DATA_CMD, 1)

        # length
        writeUInt8(cmd, 32, 3)

        # data
        writeUInt8(cmd, len(data), 4)
        copy(data, cmd, 5)

        # debug('set scan response data - writing: ' + cmd.toString('hex'))
        # print('set scan response data - writing: ' + `[hex(c) for c in cmd]`)
        self.write(cmd)

    def setAdvertiseEnable(self, enabled):
        cmd = array.array('B', [0] * 5)

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, LE_SET_ADVERTISE_ENABLE_CMD, 1)

        # length
        writeUInt8(cmd, 0x01, 3)

        # data
        writeUInt8(cmd, 0x01 if enabled else 0x00, 4)  # enable: 0 -> disabled, 1 -> enabled
        # struct.pack_into("<BHBB", cmd, 0, HCI_COMMAND_PKT, LE_SET_ADVERTISE_ENABLE_CMD, 0x01, 0x01 if enabled else 0x00 )

        # debug('set advertise enable - writing: ' + cmd.toString('hex'))
        self.write(cmd)

    def disconnect(self, handle, reason=None):
        cmd = array.array('B', [0] * 7)

        reason = reason or HCI_OE_USER_ENDED_CONNECTION

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, DISCONNECT_CMD, 1)

        # length
        writeUInt8(cmd, 0x03, 3)

        # data
        writeUInt16LE(cmd, handle, 4)  # handle
        writeUInt8(cmd, reason, 6)  # reason

        # debug('disconnect - writing: ' + cmd.toString('hex'))
        self.write(cmd)

    def readRssi(self, handle):
        cmd = array.array('B', [0] * 6)

        # header
        writeUInt8(cmd, HCI_COMMAND_PKT, 0)
        writeUInt16LE(cmd, READ_RSSI_CMD, 1)

        # length
        writeUInt8(cmd, 0x02, 3)

        # data
        writeUInt16LE(cmd, handle, 4)  # handle

        # debug('read rssi - writing: ' + cmd.toString('hex'))
        self.write(cmd)

    def writeAclDataPkt(self, handle, cid, data):
        pkt = array.array('B', [0] * (9 + len(data)))

        # header
        writeUInt8(pkt, HCI_ACLDATA_PKT, 0)
        writeUInt16LE(pkt, handle | ACL_START_NO_FLUSH << 12, 1)
        writeUInt16LE(pkt, len(data) + 4, 3)  # data length 1
        writeUInt16LE(pkt, len(data), 5)  # data length 2
        writeUInt16LE(pkt, cid, 7)

        copy(data, pkt, 9)

        # debug('write acl data pkt - writing: ' + pkt.toString('hex'))
        self.write(pkt)

    def write(self, pkt):
        # print 'WRITING: %s' % ''.join(format(x, '02x') for x in pkt)
        self._socket.write(pkt)

    def onSocketData(self, data):
        # print 'READING: %s' % ''.join(format(x, '02x') for x in data)
        # print 'got data!'
        # print [hex(c) for c in data]
        # s = struct.Struct('B')
        # unpacked_data = s.unpack(data)
        # print char.from_bytes(data)

        # eventType = data.readUInt8(0)
        # handle
        eventType = data[0]

        # debug('\tevent type = ' + eventType)
        # print('\tevent type = ' + `eventType`)

        if HCI_EVENT_PKT == eventType:
            subEventType = readUInt8(data, 1)

            # debug('\tsub event type = ' + subEventType)
            # print('\t\tsub event type = ' + `subEventType`)

            if subEventType == EVT_DISCONN_COMPLETE:
                handle = readUInt16LE(data, 4)

                reason = readUInt8(data, 6)

                # debug('\t\thandle = ' + handle)
                # debug('\t\treason = ' + reason)
                # print('\t\thandle = ' + `handle`)
                # print('\t\treason = ' + `reason`)

                self.emit('disconnComplete', [handle, reason])

            elif subEventType == EVT_ENCRYPT_CHANGE:
                handle = readUInt16LE(data, 4)
                encrypt = readUInt8(data, 6)

                # debug('\t\thandle = ' + handle)
                # debug('\t\tencrypt = ' + encrypt)
                self.emit('encryptChange', [handle, encrypt])
            elif subEventType == EVT_CMD_COMPLETE:
                # cmd = data.readUInt16LE(4)
                cmd = readUInt16LE(data, 4)
                # status = data.readUInt8(6)
                status = readUInt8(data, 6)
                # result = data.slice(7)
                result = data[7:]

                # debug('\t\tcmd = ' + cmd)
                # debug('\t\tstatus = ' + status)
                # debug('\t\tresult = ' + result.toString('hex'))
                # print('\t\tcmd = ' + `cmd`)
                # print('\t\tstatus = ' + `status`)
                # print('\t\tresult = ' + `result`);                

                self.processCmdCompleteEvent(cmd, status, result)
            elif subEventType == EVT_LE_META_EVENT:
                leMetaEventType = readUInt8(data, 3)
                leMetaEventStatus = readUInt8(data, 4)
                leMetaEventData = data[5:]

                # debug('\t\tLE meta event type = ' + leMetaEventType)
                # debug('\t\tLE meta event status = ' + leMetaEventStatus)
                # debug('\t\tLE meta event data = ' + leMetaEventData.toString('hex'))

                self.processLeMetaEvent(leMetaEventType, leMetaEventStatus, leMetaEventData)
        elif HCI_ACLDATA_PKT == eventType:
            flags = readUInt16LE(data, 1) >> 12
            handle = readUInt16LE(data, 1) & 0x0fff

            if ACL_START == flags:
                cid = readUInt16LE(data, 7)

                length = readUInt16LE(data, 5)
                pktData = data[9:]

                # debug('\t\tcid = ' + cid)

                if length == len(pktData):
                    # debug('\t\thandle = ' + handle)
                    # debug('\t\tdata = ' + pktData.toString('hex'))

                    self.emit('aclDataPkt', [handle, cid, pktData])
                else:
                    self._handleBuffers[handle] = {
                        'length': length,
                        'cid':    cid,
                        'data':   pktData
                    }
            elif ACL_CONT == flags:
                if not handle in self._handleBuffers or not 'data' in self._handleBuffers[handle]:
                    return
                self._handleBuffers[handle]['data'] = self._handleBuffers[handle]['data'] + data[5:]

                if len(self._handleBuffers[handle]['data']) == self._handleBuffers[handle]['length']:
                    self.emit('aclDataPkt',
                              [handle, self._handleBuffers[handle]['cid'], self._handleBuffers[handle]['data']])

                    del self._handleBuffers[handle]

        # print 'READ: %s' % ''.join(format(x, '02x') for x in data)

    def onSocketError(self, error):
        # debug('onSocketError: ' + error.message);
        if error.message == 'Operation not permitted':
            self.emit('stateChange', ['unauthorized'])
        elif error.message == 'Network is down':
            pass  # no-op

    def processCmdCompleteEvent(self, cmd, status, result):
        # handle
        if cmd == RESET_CMD:
            self.setEventMask()
            self.setLeEventMask()
            self.readLocalVersion()
            self.writeLeHostSupported()
            self.readLeHostSupported()
            self.readBdAddr()
        elif cmd == READ_LE_HOST_SUPPORTED_CMD:
            if status == 0:
                le = readUInt8(result, 0)
                simul = readUInt8(result, 1)

            #     debug('\t\t\tle = ' + le)
            #     debug('\t\t\tsimul = ' + simul)
        elif cmd == READ_LOCAL_VERSION_CMD:
            hciVer = readUInt8(result, 0)
            hciRev = readUInt16LE(result, 1)
            lmpVer = readInt8(result, 3)
            manufacturer = readUInt16LE(result, 4)
            lmpSubVer = readUInt16LE(result, 6)

            if hciVer < 0x06:
                self.emit('stateChange', 'unsupported')
            elif self._state != 'poweredOn':
                self.setAdvertiseEnable(False)
                self.setAdvertisingParameters()

            self.emit('readLocalVersion', [hciVer, hciRev, lmpVer, manufacturer, lmpSubVer])

        elif cmd == READ_BD_ADDR_CMD:
            self.addressType = 'public'
            # self.address = hex(result).match(/.{1,2}/g).reverse().join(':')
            self.address = "%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", result)
            # debug('address = ' + this.address)

            self.emit('addressChange', [self.address])
        elif cmd == LE_SET_ADVERTISING_PARAMETERS_CMD:
            self.emit('stateChange', ['poweredOn'])

            self.emit('leAdvertisingParametersSet', [status])
        elif cmd == LE_SET_ADVERTISING_DATA_CMD:
            self.emit('leAdvertisingDataSet', [status])
        elif cmd == LE_SET_SCAN_RESPONSE_DATA_CMD:
            self.emit('leScanResponseDataSet', [status])
        elif cmd == LE_SET_ADVERTISE_ENABLE_CMD:
            self.emit('leAdvertiseEnableSet', [status])
        elif cmd == READ_RSSI_CMD:
            handle = readUInt16LE(result, 0)
            rssi = readInt8(result, 2)

            # debug('\t\t\thandle = ' + handle)
            # debug('\t\t\trssi = ' + rssi)
            # print('\t\t\thandle = ' + `handle`)
            # print('\t\t\trssi = ' + `rssi`);            

            self.emit('rssiRead', [handle, rssi])
        elif cmd == LE_LTK_NEG_REPLY_CMD:
            handle = readUInt16LE(result, 0)

            # debug('\t\t\thandle = ' + handle)
            self.emit('leLtkNegReply', [handle])

    def processLeMetaEvent(self, eventType, status, data):
        if eventType == EVT_LE_CONN_COMPLETE:
            self.processLeConnComplete(status, data)
        elif eventType == EVT_LE_CONN_UPDATE_COMPLETE:
            self.processLeConnUpdateComplete(status, data)

    def processLeConnComplete(self, status, data):
        handle = readUInt16LE(data, 0)
        role = readUInt8(data, 2)
        addressType = 'random' if readUInt8(data, 3) == 0x01 else 'public'
        mac_data = data[4:10]
        mac_data.reverse()
        address = "%02x:%02x:%02x:%02x:%02x:%02x" % struct.unpack("BBBBBB", mac_data)
        interval = readUInt16LE(data, 10) * 1.25
        latency = readUInt16LE(data, 12)  # TODO: multiplier?
        supervisionTimeout = readUInt16LE(data, 14) * 10
        masterClockAccuracy = readUInt8(data, 16)  # TODO: multiplier?

        # debug('\t\t\thandle = ' + handle)
        # debug('\t\t\trole = ' + role)
        # debug('\t\t\taddress type = ' + addressType)
        # debug('\t\t\taddress = ' + address)
        # debug('\t\t\tinterval = ' + interval)
        # debug('\t\t\tlatency = ' + latency)
        # debug('\t\t\tsupervision timeout = ' + supervisionTimeout)
        # debug('\t\t\tmaster clock accuracy = ' + masterClockAccuracy)

        self.emit('leConnComplete', [status, handle, role, addressType, address, interval, latency, supervisionTimeout,
                                     masterClockAccuracy])

    def processLeConnUpdateComplete(self, status, data):
        handle = readUInt16LE(data, 0)
        interval = readUInt16LE(data, 2) * 1.25
        latency = readUInt16LE(data, 4)  # # TODO: multiplier?
        supervisionTimeout = readUInt16LE(data, 6) * 10

        # debug('\t\t\thandle = ' + handle)
        # debug('\t\t\tinterval = ' + interval)
        # debug('\t\t\tlatency = ' + latency)
        # debug('\t\t\tsupervision timeout = ' + supervisionTimeout)

        self.emit('leConnUpdateComplete', [status, handle, interval, latency, supervisionTimeout])

    def onStateChange(self, state):
        self._state = state

    def isDevUp(self):
        # for line in iter(popen("hciconfig").readline, ''):
        #     if "UP RUNNING" in line:
        #         return True
        # return False
        pass

    def on_socket_started(self):
        isDevUp = True  # self.isDevUp()
        if self._isDevUp != isDevUp:
            self._isDevUp = isDevUp
            if isDevUp:
                self.setSocketFilter()
                self.setEventMask()
                self.setLeEventMask()
                self.readLocalVersion()
                self.writeLeHostSupported()
                self.readLeHostSupported()
                self.readBdAddr()
            else:
                self.emit('stateChange', ['poweredOff'])

    def _socket_up_poller(self):
        while True:
            # print(self._socket.get_device_info())
            # self._socket.device_up()
            # print(popen("hciconfig").read())
            # print(popen("hciconfig").read())
            isDevUp = self.isDevUp()

            if self._isDevUp != isDevUp:
                pass
                # self._isDevUp = isDevUp
                # if isDevUp:
                #     self.setSocketFilter()
                #     self._socket.start()
                #     def do():

                #         self.setEventMask()
                #         self.setLeEventMask()
                #         self.readLocalVersion()
                #         self.writeLeHostSupported()
                #         self.readLeHostSupported()
                #         self.readBdAddr()
                #     # # self._socket.invoke(do)
                #     do()
                #     #self.emit('stateChange', ['poweredOn'])
                #     pass
                # else:
                #     self.emit('stateChange', ['poweredOff'])

            time.sleep(1)
        # setTimeout(this.pollIsDevUp.bind(this), 1000);


Emit.Patch(Hci)
