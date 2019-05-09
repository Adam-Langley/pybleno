from . import Emit
import os
import platform
import array
from .Io import *
from math import *

ATT_OP_ERROR = 0x01
ATT_OP_MTU_REQ = 0x02
ATT_OP_MTU_RESP = 0x03
ATT_OP_FIND_INFO_REQ = 0x04
ATT_OP_FIND_INFO_RESP = 0x05
ATT_OP_FIND_BY_TYPE_REQ = 0x06
ATT_OP_FIND_BY_TYPE_RESP = 0x07
ATT_OP_READ_BY_TYPE_REQ = 0x08
ATT_OP_READ_BY_TYPE_RESP = 0x09
ATT_OP_READ_REQ = 0x0a
ATT_OP_READ_RESP = 0x0b
ATT_OP_READ_BLOB_REQ = 0x0c
ATT_OP_READ_BLOB_RESP = 0x0d
ATT_OP_READ_MULTI_REQ = 0x0e
ATT_OP_READ_MULTI_RESP = 0x0f
ATT_OP_READ_BY_GROUP_REQ = 0x10
ATT_OP_READ_BY_GROUP_RESP = 0x11
ATT_OP_WRITE_REQ = 0x12
ATT_OP_WRITE_RESP = 0x13
ATT_OP_WRITE_CMD = 0x52
ATT_OP_PREP_WRITE_REQ = 0x16
ATT_OP_PREP_WRITE_RESP = 0x17
ATT_OP_EXEC_WRITE_REQ = 0x18
ATT_OP_EXEC_WRITE_RESP = 0x19
ATT_OP_HANDLE_NOTIFY = 0x1b
ATT_OP_HANDLE_IND = 0x1d
ATT_OP_HANDLE_CNF = 0x1e
ATT_OP_SIGNED_WRITE_CMD = 0xd2

GATT_PRIM_SVC_UUID = 0x2800
GATT_INCLUDE_UUID = 0x2802
GATT_CHARAC_UUID = 0x2803

GATT_CLIENT_CHARAC_CFG_UUID = 0x2902
GATT_SERVER_CHARAC_CFG_UUID = 0x2903

ATT_ECODE_SUCCESS = 0x00
ATT_ECODE_INVALID_HANDLE = 0x01
ATT_ECODE_READ_NOT_PERM = 0x02
ATT_ECODE_WRITE_NOT_PERM = 0x03
ATT_ECODE_INVALID_PDU = 0x04
ATT_ECODE_AUTHENTICATION = 0x05
ATT_ECODE_REQ_NOT_SUPP = 0x06
ATT_ECODE_INVALID_OFFSET = 0x07
ATT_ECODE_AUTHORIZATION = 0x08
ATT_ECODE_PREP_QUEUE_FULL = 0x09
ATT_ECODE_ATTR_NOT_FOUND = 0x0a
ATT_ECODE_ATTR_NOT_LONG = 0x0b
ATT_ECODE_INSUFF_ENCR_KEY_SIZE = 0x0c
ATT_ECODE_INVAL_ATTR_VALUE_LEN = 0x0d
ATT_ECODE_UNLIKELY = 0x0e
ATT_ECODE_INSUFF_ENC = 0x0f
ATT_ECODE_UNSUPP_GRP_TYPE = 0x10
ATT_ECODE_INSUFF_RESOURCES = 0x11

ATT_CID = 0x0004


class Gatt:
    def __init__(self):
        self.maxMtu = 256
        self._mtu = 23
        self._preparedWriteRequest = None
        self._aclStream = None

        self.setServices([])

    def setServices(self, services):
        deviceName = os.getenv('BLENO_DEVICE_NAME', platform.node())

        # // base services and characteristics
        allServices = [
                          {
                              'uuid':            '1800',
                              'characteristics': [
                                  {
                                      'uuid':        '2a00',
                                      'properties':  ['read'],
                                      'secure':      [],
                                      'value':       array.array('B', [ord(elem) for elem in deviceName]),
                                      'descriptors': []
                                  },
                                  {
                                      'uuid':        '2a01',
                                      'properties':  ['read'],
                                      'secure':      [],
                                      'value':       array.array('B', [0x80, 0x00]),
                                      'descriptors': []
                                  }
                              ]
                          },
                          {
                              'uuid':            '1801',
                              'characteristics': [
                                  {
                                      'uuid':        '2a05',
                                      'properties':  ['indicate'],
                                      'secure':      [],
                                      'value':       array.array('B', [0x00, 0x00, 0x00, 0x00]),
                                      'descriptors': []
                                  }
                              ]
                          }
                      ] + services

        handles = {}
        handle = 0

        for service in allServices:
            handle += 1
            serviceHandle = handle

            handles[handle] = {
                'type':        'service',
                'uuid':        service['uuid'],
                'attribute':   service,
                'startHandle': serviceHandle
                # endHandle filled in below
            }

            for characteristic in service['characteristics']:
                properties = 0
                secure = 0

                if 'read' in characteristic['properties']:
                    properties |= 0x02

                if 'read' in characteristic['secure']:
                    secure |= 0x02

                if 'writeWithoutResponse' in characteristic['properties']:
                    properties |= 0x04
                    if 'writeWithoutResponse' in characteristic['secure']:
                        secure |= 0x04

                if 'write' in characteristic['properties']:
                    properties |= 0x08

                    if 'write' in characteristic['secure']:
                        secure |= 0x08

                if 'notify' in characteristic['properties']:
                    properties |= 0x10

                    if 'notify' in characteristic['secure']:
                        secure |= 0x10

                if 'indicate' in characteristic['properties']:
                    properties |= 0x20

                    if 'indicate' in characteristic['secure']:
                        secure |= 0x20

                handle += 1
                characteristicHandle = handle

                handle += 1
                characteristicValueHandle = handle

                handles[characteristicHandle] = {
                    'type':        'characteristic',
                    'uuid':        characteristic['uuid'],
                    'properties':  properties,
                    'secure':      secure,
                    'attribute':   characteristic,
                    'startHandle': characteristicHandle,
                    'valueHandle': characteristicValueHandle
                }

                handles[characteristicValueHandle] = {
                    'type':   'characteristicValue',
                    'handle': characteristicValueHandle,
                    'value':  characteristic['value']
                }

                if properties & 0x30:  # notify or indicate
                    # add client characteristic configuration descriptor

                    handle += 1
                    clientCharacteristicConfigurationDescriptorHandle = handle
                    handles[clientCharacteristicConfigurationDescriptorHandle] = {
                        'type':       'descriptor',
                        'handle':     clientCharacteristicConfigurationDescriptorHandle,
                        'uuid':       '2902',
                        'attribute':  characteristic,
                        'properties': (0x02 | 0x04 | 0x08),  # read/write
                        'secure':     (0x02 | 0x04 | 0x08) if (secure & 0x10) else 0,
                        'value':      array.array('B', [0x00, 0x00])
                    }

                for descriptor in characteristic['descriptors']:
                    handle += 1
                    descriptorHandle = handle

                    handles[handle] = {
                        'type':       'descriptor',
                        'handle':     descriptorHandle,
                        'uuid':       descriptor.uuid,
                        'attribute':  descriptor,
                        'properties': 0x02,  # read only
                        'secure':     0x00,
                        'value':      descriptor.value
                    }

            handles[serviceHandle]['endHandle'] = handle
        self._handles = handles

    def setAclStream(self, aclStream):
        self._mtu = 23
        self._preparedWriteRequest = None

        self._aclStream = aclStream

        self._aclStream.on('data', self.onAclStreamData)
        self._aclStream.on('end', self.onAclStreamEnd)

    def onAclStreamData(self, cid, data):
        if cid != ATT_CID:
            return

        self.handleRequest(data)

    def onAclStreamEnd(self):
        self._aclStream.off('data', self.onAclStreamData)
        self._aclStream.removeListener('end', self.onAclStreamEnd)

        for i in range(0, len(self._handles)):
            if (i in self._handles and self._handles[i]['type'] == 'descriptor' and self._handles[i][
                'uuid'] == '2902' and readUInt16LE(self._handles[i]['value'], 0) != 0):

                self._handles[i]['value'] = array.array('B', [0x00, 0x00])

                if self._handles[i]['attribute'] and self._handles[i]['attribute'].emit:
                    self._handles[i]['attribute'].emit('unsubscribe', [])

    def send(self, data):
        # debug('send: ' + data.toString('hex'))
        self._aclStream.write(ATT_CID, data)

    def errorResponse(self, opcode, handle, status):
        buf = array.array('B', [0] * 5)

        writeUInt8(buf, ATT_OP_ERROR, 0)
        writeUInt8(buf, opcode, 1)
        writeUInt16LE(buf, handle, 2)
        writeUInt8(buf, status, 4)

        return buf

    def handleRequest(self, request):
        # debug('handing request: ' + request.toString('hex'))

        requestType = request[0]

        if requestType == ATT_OP_MTU_REQ:
            response = self.handleMtuRequest(request)
        elif requestType == ATT_OP_FIND_INFO_REQ:
            response = self.handleFindInfoRequest(request)
        elif requestType == ATT_OP_FIND_BY_TYPE_REQ:
            response = self.handleFindByTypeRequest(request)
        elif requestType == ATT_OP_READ_BY_TYPE_REQ:
            response = self.handleReadByTypeRequest(request)
        elif requestType == ATT_OP_READ_REQ or requestType == ATT_OP_READ_BLOB_REQ:
            response = self.handleReadOrReadBlobRequest(request)
        elif requestType == ATT_OP_READ_BY_GROUP_REQ:
            response = self.handleReadByGroupRequest(request)
        elif requestType == ATT_OP_WRITE_REQ or requestType == ATT_OP_WRITE_CMD:
            response = self.handleWriteRequestOrCommand(request)
        elif requestType == ATT_OP_PREP_WRITE_REQ:
            response = self.handlePrepareWriteRequest(request)
        elif requestType == ATT_OP_EXEC_WRITE_REQ:
            response = self.handleExecuteWriteRequest(request)
        elif requestType == ATT_OP_HANDLE_CNF:
            response = self.handleConfirmation(request)
        else:
            # case ATT_OP_READ_MULTI_REQ:
            # case ATT_OP_SIGNED_WRITE_CMD:
            response = self.errorResponse(requestType, 0x0000, ATT_ECODE_REQ_NOT_SUPP)

        if response:
            # debug('response: ' + response.toString('hex'))

            self.send(response)

    def handleMtuRequest(self, request):
        mtu = readUInt16LE(request, 1)

        if mtu < 23:
            mtu = 23
        elif mtu > self.maxMtu:
            mtu = self.maxMtu

        self._mtu = mtu

        self.emit('mtuChange', [self._mtu])

        response = array.array('B', [0] * 3)

        writeUInt8(response, ATT_OP_MTU_RESP, 0)
        writeUInt16LE(response, mtu, 1)

        return response

    def handleFindInfoRequest(self, request):
        startHandle = readUInt16LE(request, 1)
        endHandle = readUInt16LE(request, 3)

        infos = []

        for i in range(startHandle, endHandle + 1):
            handle = self._handles[i] if i in self._handles else None

            if not handle:
                break

            uuid = None

            if 'service' == handle['type']:
                uuid = '2800'
            elif 'includedService' == handle['type']:
                uuid = '2802'
            elif 'characteristic' == handle['type']:
                uuid = '2803'
            elif 'characteristicValue' == handle['type']:
                uuid = self._handles[i - 1]['uuid']
            elif 'descriptor' == handle['type']:
                uuid = handle['uuid']

            if uuid:
                infos.append({
                    'handle': i,
                    'uuid':   uuid
                })

        if len(infos):
            uuidSize = len(infos[0]['uuid']) / 2
            numInfo = 1

            for i in range(1, len(infos)):
                if not len(infos[0]['uuid']) == len(infos[i]['uuid']):
                    break
                numInfo += 1

            lengthPerInfo = 4 if (uuidSize == 2) else 18
            maxInfo = int(floor((self._mtu - 2) / lengthPerInfo))
            numInfo = min(numInfo, maxInfo)

            response = array.array('B', [0] * (2 + numInfo * lengthPerInfo))

            response[0] = ATT_OP_FIND_INFO_RESP
            response[1] = 0x01 if (uuidSize == 2) else 0x2

            for i in range(0, numInfo):
                info = infos[i]

                writeUInt16LE(response, info['handle'], 2 + i * lengthPerInfo)

                # uuid = array.array('B', info.uuid.match(/.{1,2}/g).reverse().join(''), 'hex')
                uuid = bytearray.fromhex(info['uuid'])
                uuid.reverse()
                for j in range(0, len(uuid)):
                    response[2 + i * lengthPerInfo + 2 + j] = uuid[j]
        else:
            response = self.errorResponse(ATT_OP_FIND_INFO_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)

        return response

    def handleFindByTypeRequest(self, request):
        startHandle = readUInt16LE(request, 1)
        endHandle = readUInt16LE(request, 3)
        # uuid = request.slice(5, 7).toString('hex').match(/.{1,2}/g).reverse().join('')
        uuid = request[5:7]
        uuid.reverse()
        uuid = ''.join(format(x, '02x') for x in uuid)

        # value = request.slice(7).toString('hex').match(/.{1,2}/g).reverse().join('')
        value = request[7:]
        value.reverse()
        value = ''.join(format(x, '02x') for x in value)

        handles = []

        for i in range(startHandle, endHandle + 1):
            handle = self._handles[i] if i in self._handles else None

            if not handle:
                break

            if '2800' == uuid and handle['type'] == 'service' and handle['uuid'] == value:
                handles.append({
                    'start': handle['startHandle'],
                    'end':   handle['endHandle']
                })

        if len(handles):
            lengthPerHandle = 4
            numHandles = len(handles)
            maxHandles = int(floor((self._mtu - 1) / lengthPerHandle))

            numHandles = min(numHandles, maxHandles)

            response = array.array('B', [0] * (1 + numHandles * lengthPerHandle))

            response[0] = ATT_OP_FIND_BY_TYPE_RESP

            for i in range(0, numHandles):
                handle = handles[i]

                writeUInt16LE(response, handle['start'], 1 + i * lengthPerHandle)
                writeUInt16LE(response, handle['end'], 1 + i * lengthPerHandle + 2)
        else:
            response = self.errorResponse(ATT_OP_FIND_BY_TYPE_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)

        return response

    def handleReadByGroupRequest(self, request):
        startHandle = readUInt16LE(request, 1)
        endHandle = readUInt16LE(request, 3)
        # uuid = request.slice(5).toString('hex').match(/.{1,2}/g).reverse().join('')
        uuid = request[5:]
        uuid.reverse()
        uuid = ''.join(format(x, '02x') for x in uuid)

        # debug('read by group: startHandle = 0x' + startHandle.toString(16) + ', endHandle = 0x' + endHandle.toString(16) + ', uuid = 0x' + uuid.toString(16))

        if '2800' == uuid or '2802' == uuid:
            services = []
            type = 'service' if ('2800' == uuid) else 'includedService'
            i = None

            for i in range(startHandle, endHandle + 1):
                handle = self._handles[i] if i in self._handles else None

                if not handle:
                    break

                if handle['type'] == type:
                    services.append(handle)

            if len(services):
                uuidSize = len(services[0]['uuid']) / 2
                numServices = 1

                for i in range(1, len(services)):
                    if len(services[0]['uuid']) != len(services[i]['uuid']):
                        break
                    numServices += 1

                lengthPerService = 6 if (uuidSize == 2) else 20
                maxServices = int(floor((self._mtu - 2) / lengthPerService))
                numServices = min(numServices, maxServices)

                response = array.array('B', [0] * (2 + numServices * lengthPerService))

                response[0] = ATT_OP_READ_BY_GROUP_RESP
                response[1] = lengthPerService

                for i in range(0, numServices):
                    service = services[i]

                    writeUInt16LE(response, service['startHandle'], 2 + i * lengthPerService)
                    writeUInt16LE(response, service['endHandle'], 2 + i * lengthPerService + 2)

                    # serviceUuid = array.array('B',service.uuid.match(/.{1,2}/g).reverse().join(''), 'hex')
                    serviceUuid = bytearray.fromhex(service['uuid'])
                    serviceUuid.reverse()
                    for j in range(0, len(serviceUuid)):
                        response[2 + i * lengthPerService + 4 + j] = serviceUuid[j]
            else:
                response = self.errorResponse(ATT_OP_READ_BY_GROUP_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)
        else:
            response = self.errorResponse(ATT_OP_READ_BY_GROUP_REQ, startHandle, ATT_ECODE_UNSUPP_GRP_TYPE)

        return response

    def handleReadByTypeRequest(self, request):
        response = None
        requestType = request[0]

        startHandle = readUInt16LE(request, 1)
        endHandle = readUInt16LE(request, 3)
        uuid_reversed = request[5:]
        uuid_reversed.reverse()
        uuid = ''.join(format(x, '02x') for x in uuid_reversed)

        if '2803' == uuid:
            characteristics = []

            for i in range(startHandle, endHandle + 1):
                handle = self._handles[i] if i in self._handles else None

                if not handle:
                    break

                if handle['type'] == 'characteristic':
                    characteristics.append(handle)

            if len(characteristics):
                uuidSize = len(characteristics[0]['uuid']) / 2
                numCharacteristics = 1

                for i in range(1, len(characteristics)):
                    if not len(characteristics[0]['uuid']) == len(characteristics[i]['uuid']):
                        break
                    numCharacteristics += 1

                lengthPerCharacteristic = 7 if uuidSize == 2 else 21
                maxCharacteristics = int(floor((self._mtu - 2) / lengthPerCharacteristic))
                numCharacteristics = min(numCharacteristics, maxCharacteristics)

                response = array.array('B', [0] * (2 + numCharacteristics * lengthPerCharacteristic))

                response[0] = ATT_OP_READ_BY_TYPE_RESP
                response[1] = lengthPerCharacteristic

                for i in range(0, numCharacteristics):
                    characteristic = characteristics[i]

                    writeUInt16LE(response, characteristic['startHandle'], 2 + i * lengthPerCharacteristic)
                    writeUInt8(response, characteristic['properties'], 2 + i * lengthPerCharacteristic + 2)
                    writeUInt16LE(response, characteristic['valueHandle'], 2 + i * lengthPerCharacteristic + 3)

                    characteristicUuid_reversed = bytearray.fromhex(characteristic['uuid'])
                    characteristicUuid_reversed.reverse()
                    characteristicUuid = array.array('B', characteristicUuid_reversed)

                    for j in range(0, len(characteristicUuid)):
                        response[2 + i * lengthPerCharacteristic + 5 + j] = characteristicUuid[j]
            else:
                response = self.errorResponse(ATT_OP_READ_BY_TYPE_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)
        else:
            handleAttribute = None
            valueHandle = None
            secure = False

            for i in range(startHandle, endHandle + 1):
                handle = self._handles[i] if i in self._handles else None

                if not handle:
                    break

                if handle['type'] == 'characteristic' and handle['uuid'] == uuid:
                    handleAttribute = handle['attribute']
                    valueHandle = handle['valueHandle']
                    secure = handle['secure'] & 0x02
                    break
                elif handle['type'] == 'descriptor' and handle['uuid'] == uuid:
                    valueHandle = i
                    secure = handle['secure'] & 0x02
                    break

            if secure and not self._aclStream.encrypted:
                response = self.errorResponse(ATT_OP_READ_BY_TYPE_REQ, startHandle, ATT_ECODE_AUTHENTICATION)
            elif valueHandle:
                def create_callback(valueHandle):
                    def callback(result, data):
                        if ATT_ECODE_SUCCESS == result:
                            dataLength = min(len(data), self._mtu - 4)
                            callbackResponse = array.array('B', [0] * (4 + dataLength))

                            callbackResponse[0] = ATT_OP_READ_BY_TYPE_RESP
                            callbackResponse[1] = dataLength + 2
                            writeUInt16LE(callbackResponse, valueHandle, 2)
                            for i in range(0, dataLength):
                                callbackResponse[4 + i] = data[i]
                        else:
                            callbackResponse = self.errorResponse(requestType, valueHandle, result)

                        # debug('read by type response: ' + callbackResponse.toString('hex'))

                        self.send(callbackResponse)

                    return callback

                callback = create_callback(valueHandle)

                data = self._handles[valueHandle]['value'] if 'value' in self._handles[valueHandle] else None

                if data:
                    callback(ATT_ECODE_SUCCESS, data)
                elif handleAttribute:
                    handleAttribute.emit('readRequest', [0, callback])
                else:
                    callback(ATT_ECODE_UNLIKELY)
            else:
                response = self.errorResponse(ATT_OP_READ_BY_TYPE_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)

        return response

    def handleReadOrReadBlobRequest(self, request):
        response = None

        requestType = request[0]
        valueHandle = readUInt16LE(request, 1)
        offset = readUInt16LE(request, 3) if (requestType == ATT_OP_READ_BLOB_REQ) else 0

        handle = self._handles[valueHandle] if valueHandle in self._handles else None

        if handle:
            result = None
            data = None
            handleType = handle['type']

            def create_callback(requestType, valueHandle):
                def callback(result, data):
                    if ATT_ECODE_SUCCESS == result:
                        dataLength = min(len(data), self._mtu - 1)
                        callbackResponse = array.array('B', [0] * (1 + dataLength))

                        callbackResponse[0] = ATT_OP_READ_BLOB_RESP if (
                                    requestType == ATT_OP_READ_BLOB_REQ) else ATT_OP_READ_RESP
                        for i in range(0, dataLength):
                            callbackResponse[1 + i] = data[i]
                    else:
                        callbackResponse = self.errorResponse(requestType, valueHandle, result)

                    # debug('read response: ' + callbackResponse.toString('hex'))

                    self.send(callbackResponse)

                return callback

            callback = create_callback(requestType, valueHandle)

            if handleType == 'service' or handleType == 'includedService':
                result = ATT_ECODE_SUCCESS
                # data = array.array(handle.uuid.match(/.{1,2}/g).reverse().join(''), 'hex')
                data = bytearray.fromhex(handle['uuid'])
                data.reverse()
            elif handleType == 'characteristic':
                # uuid = array.array(handle.uuid.match(/.{1,2}/g).reverse().join(''), 'hex')
                uuid = bytearray.fromhex(handle['uuid'])
                uuid.reverse()
                result = ATT_ECODE_SUCCESS
                data = array.array('B', [0] * (3 + len(uuid)))
                writeUInt8(data, handle['properties'], 0)
                writeUInt16LE(data, handle['valueHandle'], 1)

                for i in range(0, len(uuid)):
                    data[i + 3] = uuid[i]
            elif handleType == 'characteristicValue' or handleType == 'descriptor':
                handleProperties = handle['properties'] if 'properties' in handle else None
                handleSecure = handle['secure'] if 'secure' in handle else None
                handleAttribute = handle['attribute'] if 'attribute' in handle else None
                if handleType == 'characteristicValue':
                    handleProperties = self._handles[valueHandle - 1]['properties']
                    handleSecure = self._handles[valueHandle - 1]['secure']
                    handleAttribute = self._handles[valueHandle - 1]['attribute']

                if handleProperties & 0x02:
                    if handleSecure & 0x02 and not self._aclStream.encrypted:
                        result = ATT_ECODE_AUTHENTICATION
                    else:
                        data = handle['value']

                        if data:
                            result = ATT_ECODE_SUCCESS
                        else:
                            handleAttribute.emit('readRequest', [offset, callback])
                else:
                    result = ATT_ECODE_READ_NOT_PERM  # non-readable

            if data and type(data) == 'str':
                data = array.array('B', data)

            if result == ATT_ECODE_SUCCESS and data and offset:
                if len(data) < offset:
                    result = ATT_ECODE_INVALID_OFFSET
                    data = None
                else:
                    data = data[offset:]

            if result is not None:
                callback(result, data)
        else:
            response = self.errorResponse(requestType, valueHandle, ATT_ECODE_INVALID_HANDLE)

        return response

    def handleWriteRequestOrCommand(self, request):
        response = None

        requestType = request[0]
        withoutResponse = (requestType == ATT_OP_WRITE_CMD)
        valueHandle = readUInt16LE(request, 1)
        data = request[3:]
        offset = 0

        handle = self._handles[valueHandle] if valueHandle in self._handles else None

        if handle:
            if handle['type'] == 'characteristicValue':
                handle = self._handles[valueHandle - 1]

            handleProperties = handle['properties'] if 'properties' in handle else None
            handleSecure = handle['secure']

            if handleProperties and ((handleProperties & 0x04) if withoutResponse else (handleProperties & 0x08)):

                def create_callback(requestType, valueHandle, withoutResponse):
                    def callback(result):
                        if not withoutResponse:
                            if ATT_ECODE_SUCCESS == result:
                                callbackResponse = array.array('B', [ATT_OP_WRITE_RESP])
                            else:
                                callbackResponse = self.errorResponse(requestType, valueHandle, result)

                            # debug('write response: ' + callbackResponse.toString('hex'))

                            self.send(callbackResponse)

                    return callback

                callback = create_callback(requestType, valueHandle, withoutResponse)

                if handleSecure & (0x04 if withoutResponse else 0x08) and not self._aclStream.encrypted:
                    response = self.errorResponse(requestType, valueHandle, ATT_ECODE_AUTHENTICATION)
                elif handle['type'] == 'descriptor' or handle['uuid'] == '2902':
                    if not len(data) == 2:
                        result = ATT_ECODE_INVAL_ATTR_VALUE_LEN
                    else:
                        value = readUInt16LE(data, 0)
                        handleAttribute = handle['attribute']

                        handle['value'] = data

                        if value & 0x0003:
                            def create_updateValueCallback(valueHandle, attribute):
                                def updateValueCallback(data):
                                    dataLength = min(len(data), self._mtu - 3)
                                    useNotify = 'notify' in attribute['properties']
                                    useIndicate = 'indicate' in attribute['properties']
                                    i = None

                                    if useNotify:
                                        notifyMessage = array.array('B', [0] * (3 + dataLength))

                                        writeUInt8(notifyMessage, ATT_OP_HANDLE_NOTIFY, 0)
                                        writeUInt16LE(notifyMessage, valueHandle, 1)

                                        for i in range(0, dataLength):
                                            notifyMessage[3 + i] = data[i]

                                        # debug('notify message: ' + notifyMessage.toString('hex'))
                                        self.send(notifyMessage)

                                        attribute.emit('notify', [])
                                    elif useIndicate:
                                        indicateMessage = array.array('B', [0] * (3 + dataLength))

                                        writeUInt8(indicateMessage, ATT_OP_HANDLE_IND, 0)
                                        writeUInt16LE(indicateMessage, valueHandle, 1)

                                        for i in range(0, dataLength):
                                            indicateMessage[3 + i] = data[i]

                                        self._lastIndicatedAttribute = attribute

                                        # debug('indicate message: ' + indicateMessage.toString('hex'))
                                        self.send(indicateMessage)

                                return updateValueCallback

                            updateValueCallback = create_updateValueCallback(valueHandle - 1, handleAttribute)

                            if hasattr(handleAttribute, 'emit'):
                                handleAttribute.emit('subscribe', [self._mtu - 3, updateValueCallback])
                        else:
                            handleAttribute.emit('unsubscribe', [])

                        result = ATT_ECODE_SUCCESS

                    callback(result)
                else:
                    handle['attribute'].emit('writeRequest', [data, offset, withoutResponse, callback])
            else:
                response = self.errorResponse(requestType, valueHandle, ATT_ECODE_WRITE_NOT_PERM)
        else:
            response = self.errorResponse(requestType, valueHandle, ATT_ECODE_INVALID_HANDLE)

        return response

    def handlePrepareWriteRequest(self, request):
        response = None

        requestType = request[0]
        valueHandle = readUInt16LE(request, 1)
        offset = readUInt16LE(request, 3)
        data = request[5:]

        handle = self._handles[valueHandle] if valueHandle in self._handles else None

        if handle:
            if handle['type'] == 'characteristicValue':
                handle = self._handles[valueHandle - 1]

                handleProperties = handle['properties'] if 'properties' in handle else None
                handleSecure = handle['secure']

                if handleProperties and (handleProperties & 0x08):
                    if (handleSecure & 0x08) and not self._aclStream.encrypted:
                        response = self.errorResponse(requestType, valueHandle, ATT_ECODE_AUTHENTICATION)
                    elif self._preparedWriteRequest:
                        if self._preparedWriteRequest['handle'] != handle:
                            response = self.errorResponse(requestType, valueHandle, ATT_ECODE_UNLIKELY)
                        elif offset == (self._preparedWriteRequest['offset'] + len(self._preparedWriteRequest['data'])):
                            self._preparedWriteRequest['data'] = self._preparedWriteRequest['data'] + data

                            response = array.array('B', [0] * len(request))
                            copy(request, response, 0)
                            response[0] = ATT_OP_PREP_WRITE_RESP
                        else:
                            response = self.errorResponse(requestType, valueHandle, ATT_ECODE_INVALID_OFFSET)
                    else:
                        self._preparedWriteRequest = {
                            'handle':      handle,
                            'valueHandle': valueHandle,
                            'offset':      offset,
                            'data':        data
                        }

                        response = array.array('B', [0] * len(request))
                        copy(request, response, 0)
                        response[0] = ATT_OP_PREP_WRITE_RESP
                else:
                    response = self.errorResponse(requestType, valueHandle, ATT_ECODE_WRITE_NOT_PERM)
            else:
                response = self.errorResponse(requestType, valueHandle, ATT_ECODE_ATTR_NOT_LONG)
        else:
            response = self.errorResponse(requestType, valueHandle, ATT_ECODE_INVALID_HANDLE)

        return response

    def handleExecuteWriteRequest(self, request):
        response = None

        requestType = request[0]
        flag = request[1]

        if self._preparedWriteRequest:
            valueHandle = self._preparedWriteRequest['valueHandle']

            if flag == 0x00:
                response = array.array('B', [ATT_OP_EXEC_WRITE_RESP])
            elif flag == 0x01:
                def create_callback(requestType, valueHandle):
                    def callback(result):
                        callbackResponse = None

                        if ATT_ECODE_SUCCESS == result:
                            callbackResponse = array.array('B', [ATT_OP_EXEC_WRITE_RESP])
                        else:
                            callbackResponse = self.errorResponse(requestType, valueHandle, result)

                        # debug('execute write response: ' + callbackResponse.toString('hex'))

                        self.send(callbackResponse)

                    return callback

                callback = create_callback(requestType, self._preparedWriteRequest['valueHandle'])

                self._preparedWriteRequest['handle']['attribute'].emit('writeRequest',
                                                                       [self._preparedWriteRequest['data'],
                                                                        self._preparedWriteRequest['offset'], False,
                                                                        callback])
            else:
                response = self.errorResponse(requestType, 0x0000, ATT_ECODE_UNLIKELY)

            self._preparedWriteRequest = None
        else:
            response = self.errorResponse(requestType, 0x0000, ATT_ECODE_UNLIKELY)

        return response

    def handleConfirmation(self, request):
        if self._lastIndicatedAttribute:
            if self._lastIndicatedAttribute.emit:
                self._lastIndicatedAttribute.emit('indicate', [])

            self._lastIndicatedAttribute = None


Emit.Patch(Gatt)
