import array
import platform
import sys
from . import UuidUtil
from .hci_socket import Emit

platform = platform.system().lower()

if platform == 'darwin':
    # import bindings = require('./mac/bindings');
    pass
elif platform == 'linux' or platform == 'freebsd' or platform == 'windows' or platform == 'android':
    # bindings = require('./hci-socket/bindings');
    from .hci_socket import *
    # bindings = hci
else:
    raise Exception('Unsupported platform')


class Error(Exception):
    def __init__(self, message):
        self.message = message


def is_callable(callback):
    if sys.version_info[0] < 3 or sys.version_info[1] >= 2:
        # Python 2.x or 3.2+
        return callable(callback)
    else:
        return hasattr(callback, '__call__')


class Bleno:
    def __init__(self):
        self.platform = 'unknown'
        self.state = 'unknown'
        self.address = 'unknown'
        self.rssi = 0
        self.mtu = 20

        self._bindings = BlenoBindings()

        self._bindings.on('stateChange', self.onStateChange)
        self._bindings.on('platform', self.onPlatform)
        self._bindings.on('addressChange', self.onAddressChange)
        self._bindings.on('advertisingStart', self.onAdvertisingStart)
        self._bindings.on('advertisingStop', self.onAdvertisingStop)
        self._bindings.on('servicesSet', self.onServicesSet)
        self._bindings.on('accept', self.onAccept)
        self._bindings.on('mtuChange', self.onMtuChange)
        self._bindings.on('disconnect', self.onDisconnect)

        self._bindings.on('rssiUpdate', self.onRssiUpdate)

    def start(self):
        self._bindings.init()

    def onPlatform(self, platform):
        self.platform = platform

    def onStateChange(self, state):
        self.state = state

        self.emit('stateChange', [state])

    def onAddressChange(self, address):
        # debug('addressChange ' + address);

        self.address = address

    def onAccept(self, clientAddress):
        # debug('accept ' + clientAddress);
        self.emit('accept', [clientAddress])

    def onMtuChange(self, mtu):
        # debug('mtu ' + mtu);

        self.mtu = mtu

        self.emit('mtuChange', [mtu])

    def onDisconnect(self, clientAddress):
        # debug('disconnect' + clientAddress);
        self.emit('disconnect', [clientAddress])

    def startAdvertising(self, name, service_uuids=None, callback=None):
        if self.state != 'poweredOn':
            error = Error('Could not start advertising, state is {0} (not poweredOn)'.format(self.state))
            if is_callable(callback):
                callback(error)
            else:
                raise error

        else:
            if callback:
                self.once('advertisingStart', [], callback)

        if service_uuids is None:
            service_uuids = []
        undashedServiceUuids = list(map(UuidUtil.removeDashes, service_uuids))

        # print 'starting advertising %s %s' % (name, undashedServiceUuids)
        self._bindings.startAdvertising(name, undashedServiceUuids)

    def startAdvertisingIBeacon(self, uuid, major, minor, measuredPower, callback=None):
        if self.state != 'poweredOn':
            error = Error('Could not start advertising, state is {0} (not poweredOn)'.format(self.state))
            if is_callable(callback):
                callback(error)
            else:
                raise error

        else:
            undashedUuid = UuidUtil.removeDashes(uuid)
            uuidData = bytearray.fromhex(undashedUuid)
            uuidDataLength = len(uuidData)
            iBeaconData = array.array('B', [0] * (uuidDataLength + 5))

            for i in range(0, uuidDataLength):
                iBeaconData[i] = uuidData[i]

            writeUInt16BE(iBeaconData, major, uuidDataLength)
            writeUInt16BE(iBeaconData, minor, uuidDataLength + 2)
            writeInt8(iBeaconData, measuredPower, uuidDataLength + 4)

            if callback:
                self.once('advertisingStart', [], callback)

            # debug('iBeacon data = ' + iBeaconData.toString('hex'));

            self._bindings.startAdvertisingIBeacon(iBeaconData)

    def startAdvertisingWithEIRData(self, advertisementData, scanData, callback=None):
        # if (typeof scanData === 'function')
        if hasattr(scanData, '__call__') is True:
            callback = scanData
            scanData = None

        if self.state != 'poweredOn':
            error = Error('Could not start advertising, state is {0} (not poweredOn)'.format(self.state))
            if is_callable(callback):
                callback(error)
            else:
                raise error

        else:
            if callback:
                self.once('advertisingStart', [], callback)

        # print 'starting advertising with EIR data %s %s' % (advertisementData, scanData)
        self._bindings.startAdvertisingWithEIRData(advertisementData, scanData)

    def onAdvertisingStart(self, error):
        # debug('advertisingStart: ' + error);
        if error:
            self.emit('advertisingStartError', [error])

        self.emit('advertisingStart', [error])

    def stopAdvertising(self, callback=None):
        if callback:
            self.once('advertisingStop', [], callback)

        self._bindings.stopAdvertising()

    def onAdvertisingStop(self):
        # debug('advertisingStop');
        self.emit('advertisingStop', [])

    def setServices(self, services, callback=None):
        if callback:
            self.once('servicesSet', [], callback)
        # print 'setting services %s' % services
        self._bindings.setServices(services)

    def onServicesSet(self, error=None):
        # debug('servicesSet');

        if error:
            self.emit('servicesSetError', [error])

        self.emit('servicesSet', [error])

    def disconnect(self):
        # debug('disconnect');
        self._bindings.disconnect()

    def updateRssi(self, callback=None):
        if callback:
            self.once('rssiUpdate', [], callback)

        self._bindings.updateRssi()

    def onRssiUpdate(self, rssi):
        self.emit('rssiUpdate', [rssi])


Emit.Patch(Bleno)
