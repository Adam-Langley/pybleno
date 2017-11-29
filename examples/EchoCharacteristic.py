from pybleno import Characteristic
import array
import struct
from builtins import str

class EchoCharacteristic(Characteristic):
    
    def __init__(self, uuid):
        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': ['read', 'write', 'notify'],
            'value': None
          })
          
        self._value = array.array('B', [0] * 0)
        self._updateValueCallback = None
          
    def onReadRequest(self, offset, callback):
        print('EchoCharacteristic - %s - onReadRequest: value = %s' % (self['uuid'], [hex(c) for c in self._value]))
        callback(Characteristic.RESULT_SUCCESS, self._value)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        self._value = data

        print('EchoCharacteristic - %s - onWriteRequest: value = %s' % (self['uuid'], [hex(c) for c in self._value]))

        if self._updateValueCallback:
            print('EchoCharacteristic - onWriteRequest: notifying');
            
            self._updateValueCallback(self._value)
        
        callback(Characteristic.RESULT_SUCCESS)
        
    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('EchoCharacteristic - onSubscribe')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('EchoCharacteristic - onUnsubscribe');
        
        self._updateValueCallback = None
        
        
    def get_cellular_network(self):
        print ("returning cell %d" % self._cell)
        return "hello"#self._cell
    
    def set_cellular_network(self, value):
        print ("setting cell %d" % value)
        self._cell = value

class LambdaCharacteristic(Characteristic):
    def __init__(self, uuid, getter = None, setter = None, description = None):
        descriptors = []
        properties = ['notify']
        self._updateValueCallback = None

        # if description is not None:
        #     descriptors.append(BlenoDescriptor(uuid = '2901', value = description))

        if getter is not None:
            properties.append('read')
            
        if setter is not None:
            properties.append('write')

        Characteristic.__init__(self, {
            'uuid': uuid,
            'properties': properties,
            'value': None,
            'descriptors': descriptors
          })

        self.__getter = getter
        self.__setter = setter
    
    def onReadRequest(self, offset, callback):
        value = self.__getter()
        encoded_value = self._encode(value)
        callback(Characteristic.RESULT_SUCCESS, encoded_value)

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        result = 0
        
        try:
            decoded_data = _unpack_U4LE(data)
            self.__setter(decoded_data)
        except ValueError:
            # no stack trace required
            raise
        except:
            print("Exception in user code:")
            traceback.print_exc(file=sys.stdout)
            raise

#        print('EchoCharacteristic - %s - onWriteRequest: value = %s' % (self['uuid'], `[hex(c) for c in self._value]`))

        if self._updateValueCallback:
            print('EchoCharacteristic - onWriteRequest: notifying');
            
            self._updateValueCallback(data)
        
        callback(Characteristic.RESULT_SUCCESS)
        
    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('EchoCharacteristic - onSubscribe')
        
        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('EchoCharacteristic - onUnsubscribe');
        
        self._updateValueCallback = None        
        
    def _pack_U4LE(self, value):
        print ('my val is %s' % value)
        result = struct.pack('<I', value)
        return result
        
    def _unpack_U4LE(self, data):
        result = 0
        for i in reversed(range(0, len(data))):
            result = result << 8 | data[i]
        return result
        
    def _encode(self, data):
        if data is None:
            return []
            
        if type(data) == type(''):
            return array.array('B', [ord(c) for c in data]) # the 'str' is required to ensure unicode is converted
        
        return array.array('B', self._pack_U4LE(data))
