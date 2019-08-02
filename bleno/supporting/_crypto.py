import os
import sys
from Crypto.Cipher import AES

from ._jshelpers import *

require(__file__, 'sys')
module = sys.modules[__name__]


# read about how to monitor a secure connection
# https://stackoverflow.com/questions/36260101/bluez-le-secure-pairing-using-elliptical-curve-diffie-hellman-from-command-line

class Cipher:
    def __init__(self, raw_cipher):
        self._raw_cipher = raw_cipher

    def update(self, data):
        if not isinstance(data, bytes):
            data = bytes(data)
        return buffer(self._raw_cipher.encrypt(data))

    def final(self):
        return []

    def setAutoPadding(self, value):
        pass

class Crypto:
    @staticmethod
    def randomBytes(length):
        return os.urandom(length)

    def createCipheriv(cipher, key, iv):
        tmp_key = bytes(key)
        return Cipher(AES.new(tmp_key, AES.MODE_ECB))


module.exports = Crypto
