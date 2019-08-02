import array
import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:15 UTC
# source: /lib/hci-socket/gatt.js
# sha256: ee65ebba00613ee71473e061ea24e841aa34ef295536dd83d91582c7a32a550c

require(__file__, 'json')
math = require(__file__, 'math')
module = exports(__name__)# jshint loopfunc: true
debug = require(__file__, '_debug')('gatt')

events = require(__file__, '_events')
os = require(__file__, '_os')
util = require(__file__, '_util')

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

class Gatt(events.EventEmitter):
  def __init__(self, *varargs):
    events.EventEmitter.__init__(self)
    self.maxMtu = 256
    self._mtu = 23
    self._preparedWriteRequest = None

    self.setServices(GrowingList([]))

    self.onAclStreamDataBinded = bind(self, self.onAclStreamData)
    self.onAclStreamEndBinded = bind(self, self.onAclStreamEnd)

  def setServices(self, services, *varargs):
    deviceName = process.env.BLENO_DEVICE_NAME or os.hostname()

    # base services and characteristics
    allServices = GrowingList([
      DotDict([
        ('uuid', '1800'),
        ('characteristics', GrowingList([
          DotDict([
            ('uuid', '2a00'),
            ('properties', GrowingList(['read'])),
            ('secure', GrowingList([])),
            ('value', buffer(deviceName)),
            ('descriptors', GrowingList([]))
          ]), 
          DotDict([
            ('uuid', '2a01'),
            ('properties', GrowingList(['read'])),
            ('secure', GrowingList([])),
            ('value', buffer(GrowingList([0x80, 0x00]))),
            ('descriptors', GrowingList([]))
          ])
        ]))
      ]), 
      DotDict([
        ('uuid', '1801'),
        ('characteristics', GrowingList([
          DotDict([
            ('uuid', '2a05'),
            ('properties', GrowingList(['indicate'])),
            ('secure', GrowingList([])),
            ('value', buffer(GrowingList([0x00, 0x00, 0x00, 0x00]))),
            ('descriptors', GrowingList([]))
          ])
        ]))
      ])
    ]) + services

    self._handles = GrowingList([])

    handle = 0
    i = None
    j = None
    i = 0
    while True:
      if not (i < len(allServices)):
        break
      service = allServices[i]

      handle += 1
      serviceHandle = handle

      self._handles[serviceHandle] = DotDict([
        ('type', 'service'),
        ('uuid', service.uuid),
        ('attribute', service),
        ('startHandle', serviceHandle)
        # endHandle filled in below
      ])
      j = 0
      while True:
        if not (j < len(service.characteristics)):
          break
        characteristic = service.characteristics[j]

        properties = 0
        secure = 0

        if indexOf(characteristic.properties, 'read') != -1:
          properties |= 0x02

          if indexOf(characteristic.secure, 'read') != -1:
            secure |= 0x02

        if indexOf(characteristic.properties, 'writeWithoutResponse') != -1:
          properties |= 0x04

          if indexOf(characteristic.secure, 'writeWithoutResponse') != -1:
            secure |= 0x04

        if indexOf(characteristic.properties, 'write') != -1:
          properties |= 0x08

          if indexOf(characteristic.secure, 'write') != -1:
            secure |= 0x08

        if indexOf(characteristic.properties, 'notify') != -1:
          properties |= 0x10

          if indexOf(characteristic.secure, 'notify') != -1:
            secure |= 0x10

        if indexOf(characteristic.properties, 'indicate') != -1:
          properties |= 0x20

          if indexOf(characteristic.secure, 'indicate') != -1:
            secure |= 0x20

        handle += 1
        characteristicHandle = handle

        handle += 1
        characteristicValueHandle = handle

        self._handles[characteristicHandle] = DotDict([
          ('type', 'characteristic'),
          ('uuid', characteristic.uuid),
          ('properties', properties),
          ('secure', secure),
          ('attribute', characteristic),
          ('startHandle', characteristicHandle),
          ('valueHandle', characteristicValueHandle)
        ])

        self._handles[characteristicValueHandle] = DotDict([
          ('type', 'characteristicValue'),
          ('handle', characteristicValueHandle),
          ('value', characteristic.value)
        ])

        if properties & 0x30: # notify or indicate
          # add client characteristic configuration descriptor
          handle += 1
          clientCharacteristicConfigurationDescriptorHandle = handle
          self._handles[clientCharacteristicConfigurationDescriptorHandle] = DotDict([
            ('type', 'descriptor'),
            ('handle', clientCharacteristicConfigurationDescriptorHandle),
            ('uuid', '2902'),
            ('attribute', characteristic),
            ('properties', (0x02 | 0x04 | 0x08)), # read/write
            ('secure', (0x02 | 0x04 | 0x08) if (secure & 0x10) else 0),
            ('value', buffer(GrowingList([0x00, 0x00])))
          ])

        k = 0
        while True:
          if not (k < len(characteristic.descriptors)):
            break
          descriptor = characteristic.descriptors[k]

          handle += 1
          descriptorHandle = handle

          self._handles[descriptorHandle] = DotDict([
            ('type', 'descriptor'),
            ('handle', descriptorHandle),
            ('uuid', descriptor.uuid),
            ('attribute', descriptor),
            ('properties', 0x02), # read only
            ('secure', 0x00),
            ('value', descriptor.value)
          ])
          k += 1
        j += 1

      self._handles[serviceHandle].endHandle = handle
      i += 1

    debugHandles = GrowingList([])
    i = 0
    while True:
      if not (i < len(self._handles)):
        break
      handle = self._handles[i]

      debugHandles[i] = DotDict([])
      for j in handle or GrowingList([]):
        if isinstance(handle[j], array.array):
          debugHandles[i][j] = 'Buffer(\'' + str(arrayToHex(handle[j])) + '\', \'hex\')' if handle[j] else None
        elif j != 'attribute':
          debugHandles[i][j] = handle[j]
      i += 1

    debug('handles = ' + str(json.dumps(debugHandles, indent = 4)))

  def setAclStream(self, aclStream, *varargs):
    self._mtu = 23
    self._preparedWriteRequest = None

    self._aclStream = aclStream

    self._aclStream.on('data', self.onAclStreamDataBinded)
    self._aclStream.on('end', self.onAclStreamEndBinded)

  def onAclStreamData(self, cid, data, *varargs):
    if cid != ATT_CID:
      return

    self.handleRequest(data)

  def onAclStreamEnd(self, *varargs):
    self._aclStream.removeListener('data', self.onAclStreamDataBinded)
    self._aclStream.removeListener('end', self.onAclStreamEndBinded)

    i = 0
    while True:
      if not (i < len(self._handles)):
        break
      if self._handles[i] and self._handles[i].type == 'descriptor' and self._handles[i].uuid == '2902' and self._handles[i].value.readUInt16LE(0) != 0:

        self._handles[i].value = buffer(GrowingList([0x00, 0x00]))

        if self._handles[i].attribute and self._handles[i].attribute.emit:
          self._handles[i].attribute.emit('unsubscribe')
      i += 1

  def send(self, data, *varargs):
    debug('send: ' + str(arrayToHex(data)))
    self._aclStream.write(ATT_CID, data)

  def errorResponse(self, opcode, handle, status, *varargs):
    buf = buffer(5)

    buf.writeUInt8(ATT_OP_ERROR, 0)
    buf.writeUInt8(opcode, 1)
    buf.writeUInt16LE(handle, 2)
    buf.writeUInt8(status, 4)

    return buf

  def handleRequest(self, request, *varargs):
    debug('handing request: ' + str(arrayToHex(request)))

    requestType = request[0]
    response = None
    for _temp11 in switch(requestType):
      if _temp11(ATT_OP_MTU_REQ):
        response = self.handleMtuRequest(request)
        break
      if _temp11(ATT_OP_FIND_INFO_REQ):
        response = self.handleFindInfoRequest(request)
        break
      if _temp11(ATT_OP_FIND_BY_TYPE_REQ):
        response = self.handleFindByTypeRequest(request)
        break
      if _temp11(ATT_OP_READ_BY_TYPE_REQ):
        response = self.handleReadByTypeRequest(request)
        break
      if _temp11(ATT_OP_READ_REQ):
        pass
      if _temp11(ATT_OP_READ_REQ) or _temp11(ATT_OP_READ_BLOB_REQ):
        response = self.handleReadOrReadBlobRequest(request)
        break
      if _temp11(ATT_OP_READ_BY_GROUP_REQ):
        response = self.handleReadByGroupRequest(request)
        break
      if _temp11(ATT_OP_WRITE_REQ):
        pass
      if _temp11(ATT_OP_WRITE_REQ) or _temp11(ATT_OP_WRITE_CMD):
        response = self.handleWriteRequestOrCommand(request)
        break
      if _temp11(ATT_OP_PREP_WRITE_REQ):
        response = self.handlePrepareWriteRequest(request)
        break
      if _temp11(ATT_OP_EXEC_WRITE_REQ):
        response = self.handleExecuteWriteRequest(request)
        break
      if _temp11(ATT_OP_HANDLE_CNF):
        response = self.handleConfirmation(request)
        break
      if _temp11(True):
        pass
      if _temp11(True) or _temp11(ATT_OP_READ_MULTI_REQ):
        pass
      if _temp11(True) or _temp11(ATT_OP_READ_MULTI_REQ) or _temp11(True) or _temp11(ATT_OP_SIGNED_WRITE_CMD):
        response = self.errorResponse(requestType, 0x0000, ATT_ECODE_REQ_NOT_SUPP)
        break


    if response:
      debug('response: ' + str(arrayToHex(response)))

      self.send(response)

  def handleMtuRequest(self, request, *varargs):
    mtu = request.readUInt16LE(1)

    if mtu < 23:
      mtu = 23
    elif mtu > self.maxMtu:
      mtu = self.maxMtu

    self._mtu = mtu

    self.emit('mtuChange', self._mtu)

    response = buffer(3)

    response.writeUInt8(ATT_OP_MTU_RESP, 0)
    response.writeUInt16LE(mtu, 1)

    return response

  def handleFindInfoRequest(self, request, *varargs):
    response = None

    startHandle = request.readUInt16LE(1)
    endHandle = request.readUInt16LE(3)

    infos = GrowingList([])
    uuid = None
    i = None
    i = startHandle
    while True:
      if not (i <= endHandle):
        break
      handle = self._handles[i]

      if not handle:
        break

      uuid = None

      if 'service' == handle.type:
        uuid = '2800'
      elif 'includedService' == handle.type:
        uuid = '2802'
      elif 'characteristic' == handle.type:
        uuid = '2803'
      elif 'characteristicValue' == handle.type:
        uuid = self._handles[i - 1].uuid
      elif 'descriptor' == handle.type:
        uuid = handle.uuid

      if uuid:
        infos.append(DotDict([
          ('handle', i),
          ('uuid', uuid)
        ]))
      i += 1

    if len(infos):
      uuidSize = len(infos[0].uuid) / 2
      numInfo = 1
      i = 1
      while True:
        if not (i < len(infos)):
          break
        if len(infos[0].uuid) != len(infos[i].uuid):
          break
        numInfo += 1
        i += 1

      lengthPerInfo = 4 if (uuidSize == 2) else 18
      maxInfo = math.floor((self._mtu - 2) / lengthPerInfo)
      numInfo = min(numInfo, maxInfo)

      response = buffer(2 + numInfo * lengthPerInfo)

      response[0] = ATT_OP_FIND_INFO_RESP
      response[1] = 0x01 if (uuidSize == 2) else 0x2
      i = 0
      while True:
        if not (i < numInfo):
          break
        info = infos[i]

        response.writeUInt16LE(info.handle, 2 + i * lengthPerInfo)

        uuid = buffer_from_hex(''.join(reverseAndReturn(re.findall('.{1,2}', info.uuid))))
        j = 0
        while True:
          if not (j < len(uuid)):
            break
          response[2 + i * lengthPerInfo + 2 + j] = uuid[j]
          j += 1
        i += 1
    else:
      response = self.errorResponse(ATT_OP_FIND_INFO_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)

    return response

  def handleFindByTypeRequest(self, request, *varargs):
    response = None

    startHandle = request.readUInt16LE(1)
    endHandle = request.readUInt16LE(3)
    uuid = ''.join(reverseAndReturn(re.findall('.{1,2}', arrayToHex(request.slice(5, 7)))))
    value = ''.join(reverseAndReturn(re.findall('.{1,2}', arrayToHex(request.slice(7)))))

    handles = GrowingList([])
    handle = None

    i = startHandle
    while True:
      if not (i <= endHandle):
        break
      handle = self._handles[i]

      if not handle:
        break

      if '2800' == uuid and handle.type == 'service' and handle.uuid == value:
        handles.append(DotDict([
          ('start', handle.startHandle),
          ('end', handle.endHandle)
        ]))
      i += 1

    if len(handles):
      lengthPerHandle = 4
      numHandles = len(handles)
      maxHandles = math.floor((self._mtu - 1) / lengthPerHandle)

      numHandles = min(numHandles, maxHandles)

      response = buffer(1 + numHandles * lengthPerHandle)

      response[0] = ATT_OP_FIND_BY_TYPE_RESP
      i = 0
      while True:
        if not (i < numHandles):
          break
        handle = handles[i]

        response.writeUInt16LE(handle.start, 1 + i * lengthPerHandle)
        response.writeUInt16LE(handle.end, 1 + i * lengthPerHandle + 2)
        i += 1
    else:
      response = self.errorResponse(ATT_OP_FIND_BY_TYPE_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)

    return response

  def handleReadByGroupRequest(self, request, *varargs):
    response = None

    startHandle = request.readUInt16LE(1)
    endHandle = request.readUInt16LE(3)
    uuid = ''.join(reverseAndReturn(re.findall('.{1,2}', arrayToHex(request.slice(5)))))

    debug('read by group: startHandle = 0x' + str(safehex(startHandle)) + ', endHandle = 0x' + str(safehex(endHandle)) + ', uuid = 0x' + safehex(uuid))

    if '2800' == uuid or '2802' == uuid:
      services = GrowingList([])
      type = 'service' if ('2800' == uuid) else 'includedService'
      i = None
      i = startHandle
      while True:
        if not (i <= endHandle):
          break
        handle = self._handles[i]

        if not handle:
          break

        if handle.type == type:
          services.append(handle)
        i += 1

      if len(services):
        uuidSize = len(services[0].uuid) / 2
        numServices = 1
        i = 1
        while True:
          if not (i < len(services)):
            break
          if len(services[0].uuid) != len(services[i].uuid):
            break
          numServices += 1
          i += 1

        lengthPerService = 6 if (uuidSize == 2) else 20
        maxServices = math.floor((self._mtu - 2) / lengthPerService)
        numServices = min(numServices, maxServices)

        response = buffer(2 + numServices * lengthPerService)

        response[0] = ATT_OP_READ_BY_GROUP_RESP
        response[1] = lengthPerService
        i = 0
        while True:
          if not (i < numServices):
            break
          service = services[i]

          response.writeUInt16LE(service.startHandle, 2 + i * lengthPerService)
          response.writeUInt16LE(service.endHandle, 2 + i * lengthPerService + 2)

          serviceUuid = buffer_from_hex(''.join(reverseAndReturn(re.findall('.{1,2}', service.uuid))))
          j = 0
          while True:
            if not (j < len(serviceUuid)):
              break
            response[2 + i * lengthPerService + 4 + j] = serviceUuid[j]
            j += 1
          i += 1
      else:
        response = self.errorResponse(ATT_OP_READ_BY_GROUP_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)
    else:
      response = self.errorResponse(ATT_OP_READ_BY_GROUP_REQ, startHandle, ATT_ECODE_UNSUPP_GRP_TYPE)

    return response

  def handleReadByTypeRequest(self, request, *varargs):
    response = None
    requestType = request[0]

    startHandle = request.readUInt16LE(1)
    endHandle = request.readUInt16LE(3)
    uuid = ''.join(reverseAndReturn(re.findall('.{1,2}', arrayToHex(request.slice(5)))))
    i = None
    handle = None

    debug('read by type: startHandle = 0x' + str(safehex(startHandle)) + ', endHandle = 0x' + str(safehex(endHandle)) + ', uuid = 0x' + safehex(uuid))

    if '2803' == uuid:
      characteristics = GrowingList([])
      i = startHandle
      while True:
        if not (i <= endHandle):
          break
        handle = self._handles[i]

        if not handle:
          break

        if handle.type == 'characteristic':
          characteristics.append(handle)
        i += 1

      if len(characteristics):
        uuidSize = len(characteristics[0].uuid) / 2
        numCharacteristics = 1
        i = 1
        while True:
          if not (i < len(characteristics)):
            break
          if len(characteristics[0].uuid) != len(characteristics[i].uuid):
            break
          numCharacteristics += 1
          i += 1

        lengthPerCharacteristic = 7 if (uuidSize == 2) else 21
        maxCharacteristics = math.floor((self._mtu - 2) / lengthPerCharacteristic)
        numCharacteristics = min(numCharacteristics, maxCharacteristics)

        response = buffer(2 + numCharacteristics * lengthPerCharacteristic)

        response[0] = ATT_OP_READ_BY_TYPE_RESP
        response[1] = lengthPerCharacteristic
        i = 0
        while True:
          if not (i < numCharacteristics):
            break
          characteristic = characteristics[i]

          response.writeUInt16LE(characteristic.startHandle, 2 + i * lengthPerCharacteristic)
          response.writeUInt8(characteristic.properties, 2 + i * lengthPerCharacteristic + 2)
          response.writeUInt16LE(characteristic.valueHandle, 2 + i * lengthPerCharacteristic + 3)

          characteristicUuid = buffer_from_hex(''.join(reverseAndReturn(re.findall('.{1,2}', characteristic.uuid))))
          j = 0
          while True:
            if not (j < len(characteristicUuid)):
              break
            response[2 + i * lengthPerCharacteristic + 5 + j] = characteristicUuid[j]
            j += 1
          i += 1
      else:
        response = self.errorResponse(ATT_OP_READ_BY_TYPE_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)
    else:
      handleAttribute = None
      valueHandle = None
      secure = False
      i = startHandle
      while True:
        if not (i <= endHandle):
          break
        handle = self._handles[i]

        if not handle:
          break

        if handle.type == 'characteristic' and handle.uuid == uuid:
          handleAttribute = handle.attribute
          valueHandle = handle.valueHandle
          secure = handle.secure & 0x02
          break
        elif handle.type == 'descriptor' and handle.uuid == uuid:
          valueHandle = i
          secure = handle.secure & 0x02
          break
        i += 1

      if secure and not self._aclStream.encrypted:
        response = self.errorResponse(ATT_OP_READ_BY_TYPE_REQ, startHandle, ATT_ECODE_AUTHENTICATION)
      elif valueHandle:
        def _temp(self, valueHandle, *varargs):
          def _temp2(self, result, data, *varargs):
            callbackResponse = None

            if ATT_ECODE_SUCCESS == result:
              dataLength = min(len(data), self._mtu - 4)
              callbackResponse = buffer(4 + dataLength)

              callbackResponse[0] = ATT_OP_READ_BY_TYPE_RESP
              callbackResponse[1] = dataLength + 2
              callbackResponse.writeUInt16LE(valueHandle, 2)
              i = 0
              while True:
                if not (i < dataLength):
                  break
                callbackResponse[4 + i] = data[i]
                i += 1
            else:
              callbackResponse = self.errorResponse(requestType, valueHandle, result)

            debug('read by type response: ' + str(arrayToHex(callbackResponse)))

            self.send(callbackResponse)
          return bind(self, _temp2)
        callback = bind(self, _temp)(valueHandle)

        data = self._handles[valueHandle].value

        if data:
          callback(ATT_ECODE_SUCCESS, data)
        elif handleAttribute:
          handleAttribute.emit('readRequest', 0, callback)
        else:
          callback(ATT_ECODE_UNLIKELY)
      else:
        response = self.errorResponse(ATT_OP_READ_BY_TYPE_REQ, startHandle, ATT_ECODE_ATTR_NOT_FOUND)

    return response

  def handleReadOrReadBlobRequest(self, request, *varargs):
    response = None

    requestType = request[0]
    valueHandle = request.readUInt16LE(1)
    offset = request.readUInt16LE(3) if (requestType == ATT_OP_READ_BLOB_REQ) else 0

    handle = self._handles[valueHandle]
    i = None

    if handle:
      result = None
      data = None
      handleType = handle.type
      def _temp3(self, requestType, valueHandle, *varargs):
        def _temp4(self, result, data, *varargs):
          callbackResponse = None

          if ATT_ECODE_SUCCESS == result:
            dataLength = min(len(data), self._mtu - 1)
            callbackResponse = buffer(1 + dataLength)

            callbackResponse[0] = ATT_OP_READ_BLOB_RESP if (requestType == ATT_OP_READ_BLOB_REQ) else ATT_OP_READ_RESP
            i = 0
            while True:
              if not (i < dataLength):
                break
              callbackResponse[1 + i] = data[i]
              i += 1
          else:
            callbackResponse = self.errorResponse(requestType, valueHandle, result)

          debug('read response: ' + str(arrayToHex(callbackResponse)))

          self.send(callbackResponse)
        return bind(self, _temp4)
      callback = bind(self, _temp3)(requestType, valueHandle)

      if handleType == 'service' or handleType == 'includedService':
        result = ATT_ECODE_SUCCESS
        data = buffer_from_hex(''.join(reverseAndReturn(re.findall('.{1,2}', handle.uuid))))
      elif handleType == 'characteristic':
        uuid = buffer_from_hex(''.join(reverseAndReturn(re.findall('.{1,2}', handle.uuid))))

        result = ATT_ECODE_SUCCESS
        data = buffer(3 + len(uuid))
        data.writeUInt8(handle.properties, 0)
        data.writeUInt16LE(handle.valueHandle, 1)
        i = 0
        while True:
          if not (i < len(uuid)):
            break
          data[i + 3] = uuid[i]
          i += 1
      elif handleType == 'characteristicValue' or handleType == 'descriptor':
        handleProperties = handle.properties
        handleSecure = handle.secure
        handleAttribute = handle.attribute
        if handleType == 'characteristicValue':
          handleProperties = self._handles[valueHandle - 1].properties
          handleSecure = self._handles[valueHandle - 1].secure
          handleAttribute = self._handles[valueHandle - 1].attribute

        if handleProperties & 0x02:
          if handleSecure & 0x02 and not self._aclStream.encrypted:
            result = ATT_ECODE_AUTHENTICATION
          else:
            data = handle.value

            if data:
              result = ATT_ECODE_SUCCESS
            else:
              handleAttribute.emit('readRequest', offset, callback)
        else:
          result = ATT_ECODE_READ_NOT_PERM # non-readable

      if data and isinstance(data, str):
        data = buffer(data)

      if result == ATT_ECODE_SUCCESS and data and offset:
        if len(data) < offset:
          result = ATT_ECODE_INVALID_OFFSET
          data = None
        else:
          data = data.slice(offset)

      if result != None:
        callback(result, data)
    else:
      response = self.errorResponse(requestType, valueHandle, ATT_ECODE_INVALID_HANDLE)

    return response

  def handleWriteRequestOrCommand(self, request, *varargs):
    response = None

    requestType = request[0]
    withoutResponse = (requestType == ATT_OP_WRITE_CMD)
    valueHandle = request.readUInt16LE(1)
    data = request.slice(3)
    offset = 0

    handle = self._handles[valueHandle]

    if handle:
      if handle.type == 'characteristicValue':
        handle = self._handles[valueHandle - 1]

      handleProperties = handle.properties
      handleSecure = handle.secure

      if handleProperties and ((handleProperties & 0x04) if withoutResponse else (handleProperties & 0x08)):
        def _temp5(self, requestType, valueHandle, withoutResponse, *varargs):
          def _temp8(self, result, *varargs):
            if not withoutResponse:
              callbackResponse = None

              if ATT_ECODE_SUCCESS == result:
                callbackResponse = buffer(GrowingList([ATT_OP_WRITE_RESP]))
              else:
                callbackResponse = self.errorResponse(requestType, valueHandle, result)

              debug('write response: ' + str(arrayToHex(callbackResponse)))

              self.send(callbackResponse)
          return bind(self, _temp8)
        callback = bind(self, _temp5)(requestType, valueHandle, withoutResponse)

        if handleSecure & (0x04 if withoutResponse else 0x08) and not self._aclStream.encrypted:
          response = self.errorResponse(requestType, valueHandle, ATT_ECODE_AUTHENTICATION)
        elif handle.type == 'descriptor' or handle.uuid == '2902':
          result = None

          if len(data) != 2:
            result = ATT_ECODE_INVAL_ATTR_VALUE_LEN
          else:
            value = data.readUInt16LE(0)
            handleAttribute = handle.attribute

            handle.value = data

            if value & 0x0003:
              def _temp6(self, valueHandle, attribute, *varargs):
                def _temp7(self, data, *varargs):
                  dataLength = min(len(data), self._mtu - 3)
                  useNotify = indexOf(attribute.properties, 'notify') != -1
                  useIndicate = indexOf(attribute.properties, 'indicate') != -1
                  i = None

                  if useNotify:
                    notifyMessage = buffer(3 + dataLength)

                    notifyMessage.writeUInt8(ATT_OP_HANDLE_NOTIFY, 0)
                    notifyMessage.writeUInt16LE(valueHandle, 1)
                    i = 0
                    while True:
                      if not (i < dataLength):
                        break
                      notifyMessage[3 + i] = data[i]
                      i += 1

                    debug('notify message: ' + str(arrayToHex(notifyMessage)))
                    self.send(notifyMessage)

                    attribute.emit('notify')
                  elif useIndicate:
                    indicateMessage = buffer(3 + dataLength)

                    indicateMessage.writeUInt8(ATT_OP_HANDLE_IND, 0)
                    indicateMessage.writeUInt16LE(valueHandle, 1)
                    i = 0
                    while True:
                      if not (i < dataLength):
                        break
                      indicateMessage[3 + i] = data[i]
                      i += 1

                    self._lastIndicatedAttribute = attribute

                    debug('indicate message: ' + str(arrayToHex(indicateMessage)))
                    self.send(indicateMessage)
                return bind(self, _temp7)
              updateValueCallback = bind(self, _temp6)(valueHandle - 1, handleAttribute)

              if handleAttribute.emit:
                handleAttribute.emit('subscribe', self._mtu - 3, updateValueCallback)
            else:
              handleAttribute.emit('unsubscribe')

            result = ATT_ECODE_SUCCESS

          callback(result)
        else:
          handle.attribute.emit('writeRequest', data, offset, withoutResponse, callback)
      else:
        response = self.errorResponse(requestType, valueHandle, ATT_ECODE_WRITE_NOT_PERM)
    else:
      response = self.errorResponse(requestType, valueHandle, ATT_ECODE_INVALID_HANDLE)

    return response

  def handlePrepareWriteRequest(self, request, *varargs):
    response = None

    requestType = request[0]
    valueHandle = request.readUInt16LE(1)
    offset = request.readUInt16LE(3)
    data = request.slice(5)

    handle = self._handles[valueHandle]

    if handle:
      if handle.type == 'characteristicValue':
        handle = self._handles[valueHandle - 1]

        handleProperties = handle.properties
        handleSecure = handle.secure

        if handleProperties and (handleProperties & 0x08):
          if (handleSecure & 0x08) and not self._aclStream.encrypted:
            response = self.errorResponse(requestType, valueHandle, ATT_ECODE_AUTHENTICATION)
          elif self._preparedWriteRequest:
            if self._preparedWriteRequest.handle != handle:
              response = self.errorResponse(requestType, valueHandle, ATT_ECODE_UNLIKELY)
            elif offset == (self._preparedWriteRequest.offset + len(self._preparedWriteRequest.data)):
              self._preparedWriteRequest.data = concat_lists(GrowingList([
                self._preparedWriteRequest.data, 
                data
              ]))

              response = buffer(len(request))
              request.copy(response)
              response[0] = ATT_OP_PREP_WRITE_RESP
            else:
              response = self.errorResponse(requestType, valueHandle, ATT_ECODE_INVALID_OFFSET)
          else:
            self._preparedWriteRequest = DotDict([
              ('handle', handle),
              ('valueHandle', valueHandle),
              ('offset', offset),
              ('data', data)
            ])

            response = buffer(len(request))
            request.copy(response)
            response[0] = ATT_OP_PREP_WRITE_RESP
        else:
          response = self.errorResponse(requestType, valueHandle, ATT_ECODE_WRITE_NOT_PERM)
      else:
        response = self.errorResponse(requestType, valueHandle, ATT_ECODE_ATTR_NOT_LONG)
    else:
      response = self.errorResponse(requestType, valueHandle, ATT_ECODE_INVALID_HANDLE)

    return response

  def handleExecuteWriteRequest(self, request, *varargs):
    response = None

    requestType = request[0]
    flag = request[1]

    if self._preparedWriteRequest:
      valueHandle = self._preparedWriteRequest.valueHandle

      if flag == 0x00:
        response = buffer(GrowingList([ATT_OP_EXEC_WRITE_RESP]))
      elif flag == 0x01:
        def _temp9(self, requestType, valueHandle, *varargs):
          def _temp10(self, result, *varargs):
            callbackResponse = None

            if ATT_ECODE_SUCCESS == result:
              callbackResponse = buffer(GrowingList([ATT_OP_EXEC_WRITE_RESP]))
            else:
              callbackResponse = self.errorResponse(requestType, valueHandle, result)

            debug('execute write response: ' + str(arrayToHex(callbackResponse)))

            self.send(callbackResponse)
          return bind(self, _temp10)
        callback = bind(self, _temp9)(requestType, self._preparedWriteRequest.valueHandle)

        self._preparedWriteRequest.handle.attribute.emit('writeRequest', self._preparedWriteRequest.data, self._preparedWriteRequest.offset, False, callback)
      else:
        response = self.errorResponse(requestType, 0x0000, ATT_ECODE_UNLIKELY)

      self._preparedWriteRequest = None
    else:
      response = self.errorResponse(requestType, 0x0000, ATT_ECODE_UNLIKELY)

    return response

  def handleConfirmation(self, request, *varargs):
    if self._lastIndicatedAttribute:
      if self._lastIndicatedAttribute.emit:
        self._lastIndicatedAttribute.emit('indicate')

      self._lastIndicatedAttribute = None

module.exports = Gatt