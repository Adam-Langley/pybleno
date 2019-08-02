import sys
from bleno.supporting import *
# This file was transpiled at: 2019-07-30 04:42:13 UTC
# source: /lib/hci-socket/crypto.js
# sha256: b33bfdf76c505fd58e74b117ca80ae7a0e208f0fe7b9b84ea88304cdbbd56dd5

math = require(__file__, 'math')
module = exports(__name__)
crypto = require(__file__, '_crypto')

def r(*varargs):
  return crypto.randomBytes(16)

def c1(k, r, pres, preq, iat, ia, rat, ra, *varargs):
  p1 = concat_lists(GrowingList([
    iat, 
    rat, 
    preq, 
    pres
  ]))

  p2 = concat_lists(GrowingList([
    ra, 
    ia, 
    buffer_from_hex('00000000')
  ]))

  res = xor(r, p1)
  res = e(k, res)
  res = xor(res, p2)
  res = e(k, res)

  return res

def s1(k, r1, r2, *varargs):
  return e(k, concat_lists(GrowingList([
    r2.slice(0, 8), 
    r1.slice(0, 8)
  ])))

def e(key, data, *varargs):
  key = swap(key)
  data = swap(data)

  cipher = crypto.createCipheriv('aes-128-ecb', key, '')
  cipher.setAutoPadding(False)

  return swap(concat_lists(GrowingList([
    cipher.update(data), 
    cipher.final()
  ])))

def xor(b1, b2, *varargs):
  result = buffer(len(b1))

  i = 0
  while True:
    if not (i < len(b1)):
      break
    result[i] = b1[i] ^ b2[i]
    i += 1

  return result

def swap(input, *varargs):
  output = buffer(len(input))

  i = 0
  while True:
    if not (i < len(output)):
      break
    output[i] = input[len(input) - i - 1]
    i += 1

  return output

module.exports = DotDict([
  ('r', r),
  ('c1', c1),
  ('s1', s1),
  ('e', e)
])