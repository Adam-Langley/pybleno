import platform
import array
from . import Emit, Hci
from .Io import *

isLinux = (platform.system() == 'Linux')
isIntelEdison = False  # isLinux && (os.release().indexOf('edison') !== -1)
isYocto = False  # isLinux && (os.release().indexOf('yocto') !== -1)


class Gap:
    def __init__(self, hci):
        self._hci = hci

        self._advertiseState = None

        self._hci.on('error', self.onHciError)

        self._hci.on('leAdvertisingParametersSet', self.onHciLeAdvertisingParametersSet)
        self._hci.on('leAdvertisingDataSet', self.onHciLeAdvertisingDataSet)
        self._hci.on('leScanResponseDataSet', self.onHciLeScanResponseDataSet)
        self._hci.on('leAdvertiseEnableSet', self.onHciLeAdvertiseEnableSet)

    def startAdvertising(self, name, serviceUuids):
        # debug('startAdvertising: name = ' + name + ', serviceUuids = ' + JSON.stringify(serviceUuids, null, 2))

        advertisementDataLength = 3
        scanDataLength = 0

        serviceUuids16bit = []
        serviceUuids128bit = []
        i = 0

        if name and len(name):
            scanDataLength += 2 + len(name)

        if serviceUuids and len(serviceUuids):
            for i in range(0, len(serviceUuids)):
                # serviceUuid = new Buffer(serviceUuids[i].match(/.{1,2}/g).reverse().join(''), 'hex')

                serviceUuid = bytearray.fromhex(serviceUuids[
                                                    i])  # struct.unpack("<H","f483")[0]#sum([(c,d,a,b) for a,b,c,d in zip(*[iter(serviceUuids[i])]*4)], ())
                serviceUuid.reverse()
                if len(serviceUuid) == 2:
                    serviceUuids16bit.append(serviceUuid)
                elif len(serviceUuid) == 16:
                    serviceUuids128bit.append(serviceUuid)

        if len(serviceUuids16bit):
            advertisementDataLength += 2 + 2 * len(serviceUuids16bit)

        if len(serviceUuids128bit):
            advertisementDataLength += 2 + 16 * len(serviceUuids128bit)

        # advertisementData = new Buffer(advertisementDataLength)
        advertisementData = array.array('B', [0] * advertisementDataLength)

        # scanData = new Buffer(scanDataLength)
        scanData = array.array('B', [0] * scanDataLength)

        # // flags
        # advertisementData.writeUInt8(2, 0)
        # advertisementData.writeUInt8(0x01, 1)
        # advertisementData.writeUInt8(0x06, 2)
        writeUInt8(advertisementData, 0x02, 0)
        writeUInt8(advertisementData, 0x01, 1)
        writeUInt8(advertisementData, 0x06, 2)

        advertisementDataOffset = 3

        if len(serviceUuids16bit):
            writeUInt8(advertisementData, 1 + 2 * len(serviceUuids16bit), advertisementDataOffset)
            advertisementDataOffset += 1

            writeUInt8(advertisementData, 0x03, advertisementDataOffset)
            advertisementDataOffset += 1

            for i in range(0, len(serviceUuids16bit)):
                copy(serviceUuids16bit[i], advertisementData, advertisementDataOffset)
                advertisementDataOffset += len(serviceUuids16bit[i])

        if len(serviceUuids128bit):
            writeUInt8(advertisementData, 1 + 16 * len(serviceUuids128bit), advertisementDataOffset)
            advertisementDataOffset += 1

            writeUInt8(advertisementData, 0x06, advertisementDataOffset)
            advertisementDataOffset += 1

            for i in range(0, len(serviceUuids128bit)):
                copy(serviceUuids128bit[i], advertisementData, advertisementDataOffset)
                advertisementDataOffset += len(serviceUuids128bit[i])

        # // name
        if name and len(name):
            nameBuffer = array.array('B', [ord(elem) for elem in name])

            writeUInt8(scanData, 1 + len(nameBuffer), 0)
            writeUInt8(scanData, 0x08, 1)
            copy(nameBuffer, scanData, 2)

        self.startAdvertisingWithEIRData(advertisementData, scanData)

    def startAdvertisingIBeacon(self, data):
        # debug('startAdvertisingIBeacon: data = ' + data.toString('hex'))

        dataLength = len(data)
        manufacturerDataLength = 4 + dataLength
        advertisementDataLength = 5 + manufacturerDataLength
        scanDataLength = 0

        advertisementData = array.array('B', [0] * advertisementDataLength)
        scanData = array.array('B', [0] * 0)

        # flags
        writeUInt8(advertisementData, 2, 0)
        writeUInt8(advertisementData, 0x01, 1)
        writeUInt8(advertisementData, 0x06, 2)

        writeUInt8(advertisementData, manufacturerDataLength + 1, 3)
        writeUInt8(advertisementData, 0xff, 4)
        writeUInt16LE(advertisementData, 0x004c, 5);  # Apple Company Identifier LE (16 bit)
        writeUInt8(advertisementData, 0x02, 7);  # type, 2 => iBeacon
        writeUInt8(advertisementData, dataLength, 8)

        copy(data, advertisementData, 9)

        self.startAdvertisingWithEIRData(advertisementData, scanData)

    def startAdvertisingWithEIRData(self, advertisementData, scanData):
        advertisementData = advertisementData or array.array('B', [0] * 0)
        scanData = scanData or array.array('B', [0] * 0)

        # debug('startAdvertisingWithEIRData: advertisement data = ' + advertisementData.toString('hex') + ', scan data = ' + scanData.toString('hex'))

        error = None

        if len(advertisementData) > 31:
            error = Exception('Advertisement data is over maximum limit of 31 bytes')
        elif len(scanData) > 31:
            error = Exception('Scan data is over maximum limit of 31 bytes')

        if error:
            self.emit('advertisingStart', [error])
        else:
            self._advertiseState = 'starting'

            if isIntelEdison or isYocto:
                # // work around for Intel Edison
                # debug('skipping first set of scan response and advertisement data')
                pass
            else:
                self._hci.setScanResponseData(scanData)
                self._hci.setAdvertisingData(advertisementData)

            self._hci.setAdvertiseEnable(True)
            self._hci.setScanResponseData(scanData)
            self._hci.setAdvertisingData(advertisementData)

    def restartAdvertising(self):
        self._advertiseState = 'restarting'

        self._hci.setAdvertiseEnable(True)

    def stopAdvertising(self):
        self._advertiseState = 'stopping'

        self._hci.setAdvertiseEnable(False)

    def onHciError(self, error):
        pass

    def onHciLeAdvertisingParametersSet(self, status):
        pass

    def onHciLeAdvertisingDataSet(self, status):
        pass

    def onHciLeScanResponseDataSet(self, status):
        pass

    def onHciLeAdvertiseEnableSet(self, status):
        if self._advertiseState == 'starting':
            self._advertiseState = 'started'

            error = None

            if status:
                error = Exception(Hci.STATUS_MAPPER[status] or ('Unknown (' + status + ')'))

            self.emit('advertisingStart', [error])
        elif self._advertiseState == 'stopping':
            self._advertiseState = 'stopped'

            self.emit('advertisingStop', [])


Emit.Patch(Gap)
