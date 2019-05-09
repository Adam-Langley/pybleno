from . import Emit
import array
from .Io import *

SMP_CID = 0x0006

SMP_PAIRING_REQUEST = 0x01
SMP_PAIRING_RESPONSE = 0x02
SMP_PAIRING_CONFIRM = 0x03
SMP_PAIRING_RANDOM = 0x04
SMP_PAIRING_FAILED = 0x05
SMP_ENCRYPT_INFO = 0x06
SMP_MASTER_IDENT = 0x07

SMP_UNSPECIFIED = 0x08


class Smp:
    def __init__(self, aclStream, localAddressType, localAddress, remoteAddressType, remoteAddress):
        self._aclStream = aclStream

        self._iat = array.array('B', [0x01 if (remoteAddressType == 'random') else 0x00])
        remoteAddressBytes = bytearray.fromhex(remoteAddress.replace(':', ''))
        remoteAddressBytes.reverse()
        self._ia = array.array('B', remoteAddressBytes)  # todo - this is wrong
        self._rat = array.array('B', [0x01 if (localAddressType == 'random') else 0x00])
        localAddressBytes = bytearray.fromhex(localAddress.replace(':', ''))
        # localAddressBytes.reverse() # for some reaon this array is already correctly reversed???
        self._ra = array.array('B', localAddressBytes)
        self._stk = None
        self._random = None
        self._diversifier = None

        self._aclStream.on('data', self.onAclStreamData)
        self._aclStream.on('encryptChange', self.onAclStreamEncryptChange)
        self._aclStream.on('ltkNegReply', self.onAclStreamLtkNegReply)
        self._aclStream.on('end', self.onAclStreamEnd)

    def onAclStreamData(self, cid, data):
        if cid != SMP_CID:
            return

        code = readUInt8(data, 0)

        if SMP_PAIRING_REQUEST == code:
            self.handlePairingRequest(data)
        elif SMP_PAIRING_CONFIRM == code:
            self.handlePairingConfirm(data)
        elif SMP_PAIRING_RANDOM == code:
            self.handlePairingRandom(data)
        elif SMP_PAIRING_FAILED == code:
            self.handlePairingFailed(data)

    def onAclStreamEncryptChange(self, encrypted):
        if encrypted:
            if self._stk and self._diversifier and self._random:
                self.write(Buffer.concat([
                    array.array('B', [SMP_ENCRYPT_INFO]),
                    self._stk
                ]))

                self.write(Buffer.concat([
                    array.array('B', [SMP_MASTER_IDENT]),
                    self._diversifier,
                    self._random
                ]))

    def onAclStreamLtkNegReply(self):
        self.write(array.array('B', [
            SMP_PAIRING_FAILED,
            SMP_UNSPECIFIED
        ]))

        self.emit('fail', [])

    def onAclStreamEnd(self):
        self._aclStream.off('data', self.onAclStreamData)
        self._aclStream.off('encryptChange', self.onAclStreamEncryptChange)
        self._aclStream.off('ltkNegReply', self.onAclStreamLtkNegReply)
        self._aclStream.off('end', self.onAclStreamEnd)

    def handlePairingRequest(self, data):
        self._preq = data

        self._pres = array.array('B', [
            SMP_PAIRING_RESPONSE,
            0x03,  # IO capability: NoInputNoOutput
            0x00,  # OOB data: Authentication data not present
            0x01,  # Authentication requirement: Bonding - No MITM
            0x10,  # Max encryption key size
            0x00,  # Initiator key distribution: <none>
            0x01  # Responder key distribution: EncKey
        ])

        self.write(self._pres)

    def handlePairingConfirm(self, data):
        self._pcnf = data

        self._tk = array.array('B', [0] * 16)
        self._r = crypto.r()

        # TODO: port this...
        # self.write(Buffer.concat([
        # new Buffer([SMP_PAIRING_CONFIRM]),
        #     crypto.c1(self._tk, self._r, self._pres, self._preq, self._iat, self._ia, self._rat, self._ra)
        # ]))

    def handlePairingRandom(self, data):
        r = data[1:]

        pcnf = Buffer.concat([
            array.array('B', [SMP_PAIRING_CONFIRM]),
            crypto.c1(self._tk, r, self._pres, self._preq, self._iat, self._ia, self._rat, self._ra)
        ])

        if self._pcnf.toString('hex') == pcnf.toString('hex'):
            self._diversifier = array.array('B', [0] * 2)
            self._random = array.array('B', [0] * 8)
            self._stk = crypto.s1(self._tk, self._r, r)

            mgmt.addLongTermKey(self._ia, self._iat, 0, 0, self._diversifier, self._random, self._stk)

            self.write(Buffer.concat([
                array.array('B', [SMP_PAIRING_RANDOM]),
                self._r
            ]))
        else:
            self.write(array.array('B', [
                SMP_PAIRING_FAILED,
                SMP_PAIRING_CONFIRM
            ]))

            self.emit('fail', [])

    def handlePairingFailed(self, data):
        self.emit('fail', [])

    def write(self, data):
        self._aclStream.write(SMP_CID, data)


Emit.Patch(Smp)
