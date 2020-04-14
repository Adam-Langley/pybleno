import os
from Crypto.Cipher import AES
import array
import numpy as np


def r():
    return os.urandom(16)

def c1(k, r, pres, preq, iat, ia, rat, ra):
    # according to corespec
    #p1 = pres + preq + rat + iat
    #p2 = array.array('B', [0] * 4) + ia + ra

    # according to node
    p1 = iat + rat + preq + pres
    p2 = ra + ia + array.array('B', [0] * 4)

    res = xor(r, p1)
    res = e(k, res)
    res = xor(res, p2)
    res = e(k, res)

    # print('k:',bytes(k).hex(), ' r:',bytes(r).hex(), ' ia:',bytes(ia).hex(), ' ra:',bytes(ra).hex(), ' iat:',bytes(iat).hex(), ' rat:',bytes(rat).hex(), ' preq:',bytes(preq).hex(), ' pres:',bytes(pres).hex(), ' p1:',bytes(p1).hex(), ' p2:',bytes(p2).hex(), 'res:',bytes(res).hex())

    return res

def s1(k, r1, r2):
    # according to corespec
    #return e(k, r1[8:] + r2[8:])

    # according to node
    return e(k, r2[:8] + r1[:8])

def e(key, data):
    # according to corespec
    #cipher = AES.new(bytes(key), AES.MODE_ECB)
    #return array.array('B', cipher.encrypt(bytes(data)))

    # according to node
    key = bytes(swap(key))
    data = bytes(swap(data))
    cipher = AES.new(key, AES.MODE_ECB)
    return swap(cipher.encrypt(data))

def xor(b1, b2):
    result = array.array('B', [0] * len(b1))

    for i in range(len(b1)):
        result[i] = b1[i] ^ b2[i]

    return result

def swap(src):
    return array.array('B', src[::-1])
