import platform
from . import UuidUtil
from .hci_socket import Emit

platform = platform.system()

if platform == 'darwin':
    #import bindings = require('./mac/bindings');
    pass
elif platform == 'Linux' or platform == 'Freebsd' or platform == 'Windows' or platform == 'Android':
    #bindings = require('./hci-socket/bindings');
    from .hci_socket import *
    #bindings = hci
else:
    raise Exception('Unsupported platform')
    
class Bleno:
    def __init__(self):
        self.platform = 'unknown'
        self.state = 'unknown'
        self.address = 'unknown'
        self.rssi = 0
        self.mtu = 20
        
        self._bindings = BlenoBindings()
        
        self._bindings.on('stateChange', self.onStateChange);
        self._bindings.on('platform', self.onPlatform);
        self._bindings.on('addressChange', self.onAddressChange);
        self._bindings.on('advertisingStart', self.onAdvertisingStart);
        self._bindings.on('advertisingStop', self.onAdvertisingStop);
        self._bindings.on('servicesSet', self.onServicesSet);
        self._bindings.on('accept', self.onAccept);
        self._bindings.on('mtuChange', self.onMtuChange);
        self._bindings.on('disconnect', self.onDisconnect);
        
        self._bindings.on('rssiUpdate', self.onRssiUpdate);
        
        self._bindings.init()
    
    def onPlatform(self, platform):
        self.platform = platform
        
    def onStateChange(self, state):
        self.state = state;
        
        self.emit('stateChange', [state]);
        
    def onAddressChange(self, address):
        #debug('addressChange ' + address);
        
        self.address = address;
    
    
    def onAccept(self, clientAddress):
        #debug('accept ' + clientAddress);
        self.emit('accept', [clientAddress]);
    
    
    def onMtuChange(self, mtu):
        #debug('mtu ' + mtu);
        
        self.mtu = mtu;
        
        self.emit('mtuChange', [mtu]);

    def onDisconnect(self, clientAddress):
        #debug('disconnect' + clientAddress);
        self.emit('disconnect', [clientAddress]);

    def startAdvertising(self, name, serviceUuids, callback=None):
        if (self.state != 'poweredOn'):
            #var error = new Error('Could not start advertising, state is ' + self.state + ' (not poweredOn)');
            
            #if (typeof callback === 'function') 
            callback(error);
            #else
            #    throw error;
            
        else:
            if (callback):
                self.once('advertisingStart', callback)
        
        
        undashedServiceUuids = []
        
        if (serviceUuids and len(serviceUuids)):
            for i in range(0, len(serviceUuids)):
                undashedServiceUuids.append(UuidUtil.removeDashes(serviceUuids[i]));
        
        #print 'starting advertising %s %s' % (name, undashedServiceUuids) 
        self._bindings.startAdvertising(name, undashedServiceUuids);
        
    def onAdvertisingStart(self, error):
        #debug('advertisingStart: ' + error);
        if error:
            self.emit('advertisingStartError', [error])
            
        self.emit('advertisingStart', [error]);

    def stopAdvertising(self, callback=None):
        if callback:
            self.once('advertisingStop', [callback])
        
        self._bindings.stopAdvertising()

    def onAdvertisingStop(self):
        # debug('advertisingStop');
        self.emit('advertisingStop', [])
    
    def setServices(self, services, callback=None):
        if callback:
            self.once('servicesSet', callback)
        #print 'setting services %s' % services
        self._bindings.setServices(services)

    def onServicesSet(self, error=None):
        #debug('servicesSet');
        
        if error:
            self.emit('servicesSetError', [error])

        self.emit('servicesSet', [error])

    def disconnect(self):
        #debug('disconnect');
        self._bindings.disconnect()
        
    def updateRssi(self, callback=None):
        if callback:
            self.once('rssiUpdate', callback)

        self._bindings.updateRssi()

    def onRssiUpdate(self, rssi):
        self.emit('rssiUpdate', [rssi]);
       
Emit.Patch(Bleno)