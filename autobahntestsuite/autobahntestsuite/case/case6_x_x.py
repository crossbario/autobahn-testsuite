# coding=utf-8

###############################################################################
##
##  Copyright (c) Crossbar.io Technologies GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import binascii
from case import Case
from autobahn.websocket.utf8validator import Utf8Validator


def createUtf8TestSequences():
   """
   Create test sequences for UTF-8 decoder tests from
   http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt
   """

   UTF8_TEST_SEQUENCES = []

   # 1 Some correct UTF-8 text
   vss = '\xce\xba\xe1\xbd\xb9\xcf\x83\xce\xbc\xce\xb5'
   vs = ["Some valid UTF-8 sequences", []]
   vs[1].append((True, 'hello\x24world')) # U+0024
   vs[1].append((True, 'hello\xC2\xA2world')) # U+00A2
   vs[1].append((True, 'hello\xE2\x82\xACworld')) # U+20AC
   vs[1].append((True, 'hello\xF0\xA4\xAD\xA2world')) # U+24B62
   vs[1].append((True, vss))
   UTF8_TEST_SEQUENCES.append(vs)

   # All prefixes of correct UTF-8 text
   vs = ["All prefixes of a valid UTF-8 string that contains multi-byte code points", []]
   v = Utf8Validator()
   for i in xrange(1, len(vss) + 1):
      v.reset()
      res = v.validate(vss[:i])
      vs[1].append((res[0] and res[1], vss[:i]))
   UTF8_TEST_SEQUENCES.append(vs)

   # 2.1 First possible sequence of a certain length
   vs = ["First possible sequence of a certain length", []]
   vs[1].append((True, '\x00'))
   vs[1].append((True, '\xc2\x80'))
   vs[1].append((True, '\xe0\xa0\x80'))
   vs[1].append((True, '\xf0\x90\x80\x80'))
   UTF8_TEST_SEQUENCES.append(vs)

   # the following conform to the UTF-8 integer encoding scheme, but
   # valid UTF-8 only allows for Unicode code points up to U+10FFFF
   vs = ["First possible sequence length 5/6 (invalid codepoints)", []]
   vs[1].append((False, '\xf8\x88\x80\x80\x80'))
   vs[1].append((False, '\xfc\x84\x80\x80\x80\x80'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 2.2 Last possible sequence of a certain length
   vs = ["Last possible sequence of a certain length", []]
   vs[1].append((True, '\x7f'))
   vs[1].append((True, '\xdf\xbf'))
   vs[1].append((True, '\xef\xbf\xbf'))
   vs[1].append((True, '\xf4\x8f\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # the following conform to the UTF-8 integer encoding scheme, but
   # valid UTF-8 only allows for Unicode code points up to U+10FFFF
   vs = ["Last possible sequence length 4/5/6 (invalid codepoints)", []]
   vs[1].append((False, '\xf7\xbf\xbf\xbf'))
   vs[1].append((False, '\xfb\xbf\xbf\xbf\xbf'))
   vs[1].append((False, '\xfd\xbf\xbf\xbf\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 2.3 Other boundary conditions
   vs = ["Other boundary conditions", []]
   vs[1].append((True, '\xed\x9f\xbf'))
   vs[1].append((True, '\xee\x80\x80'))
   vs[1].append((True, '\xef\xbf\xbd'))
   vs[1].append((True, '\xf4\x8f\xbf\xbf'))
   vs[1].append((False, '\xf4\x90\x80\x80'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.1  Unexpected continuation bytes
   vs = ["Unexpected continuation bytes", []]
   vs[1].append((False, '\x80'))
   vs[1].append((False, '\xbf'))
   vs[1].append((False, '\x80\xbf'))
   vs[1].append((False, '\x80\xbf\x80'))
   vs[1].append((False, '\x80\xbf\x80\xbf'))
   vs[1].append((False, '\x80\xbf\x80\xbf\x80'))
   vs[1].append((False, '\x80\xbf\x80\xbf\x80\xbf'))
   s = ""
   for i in xrange(0x80, 0xbf):
      s += chr(i)
   vs[1].append((False, s))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.2  Lonely start characters
   vs = ["Lonely start characters", []]
   m = [(0xc0, 0xdf), (0xe0, 0xef), (0xf0, 0xf7), (0xf8, 0xfb), (0xfc, 0xfd)]
   for mm in m:
      s = ''
      for i in xrange(mm[0], mm[1]):
         s += chr(i)
         s += chr(0x20)
      vs[1].append((False, s))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.3  Sequences with last continuation byte missing
   vs = ["Sequences with last continuation byte missing", []]
   k = ['\xc0', '\xe0\x80', '\xf0\x80\x80', '\xf8\x80\x80\x80', '\xfc\x80\x80\x80\x80',
        '\xdf', '\xef\xbf', '\xf7\xbf\xbf', '\xfb\xbf\xbf\xbf', '\xfd\xbf\xbf\xbf\xbf']
   for kk in k:
      vs[1].append((False, kk))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.4  Concatenation of incomplete sequences
   vs = ["Concatenation of incomplete sequences", []]
   vs[1].append((False, ''.join(k)))
   UTF8_TEST_SEQUENCES.append(vs)

   # 3.5  Impossible bytes
   vs = ["Impossible bytes", []]
   vs[1].append((False, '\xfe'))
   vs[1].append((False, '\xff'))
   vs[1].append((False, '\xfe\xfe\xff\xff'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 4.1  Examples of an overlong ASCII character
   vs = ["Examples of an overlong ASCII character", []]
   vs[1].append((False, '\xc0\xaf'))
   vs[1].append((False, '\xe0\x80\xaf'))
   vs[1].append((False, '\xf0\x80\x80\xaf'))
   vs[1].append((False, '\xf8\x80\x80\x80\xaf'))
   vs[1].append((False, '\xfc\x80\x80\x80\x80\xaf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 4.2  Maximum overlong sequences
   vs = ["Maximum overlong sequences", []]
   vs[1].append((False, '\xc1\xbf'))
   vs[1].append((False, '\xe0\x9f\xbf'))
   vs[1].append((False, '\xf0\x8f\xbf\xbf'))
   vs[1].append((False, '\xf8\x87\xbf\xbf\xbf'))
   vs[1].append((False, '\xfc\x83\xbf\xbf\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 4.3  Overlong representation of the NUL character
   vs = ["Overlong representation of the NUL character", []]
   vs[1].append((False, '\xc0\x80'))
   vs[1].append((False, '\xe0\x80\x80'))
   vs[1].append((False, '\xf0\x80\x80\x80'))
   vs[1].append((False, '\xf8\x80\x80\x80\x80'))
   vs[1].append((False, '\xfc\x80\x80\x80\x80\x80'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 5.1 Single UTF-16 surrogates
   vs = ["Single UTF-16 surrogates", []]
   vs[1].append((False, '\xed\xa0\x80'))
   vs[1].append((False, '\xed\xad\xbf'))
   vs[1].append((False, '\xed\xae\x80'))
   vs[1].append((False, '\xed\xaf\xbf'))
   vs[1].append((False, '\xed\xb0\x80'))
   vs[1].append((False, '\xed\xbe\x80'))
   vs[1].append((False, '\xed\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 5.2 Paired UTF-16 surrogates
   vs = ["Paired UTF-16 surrogates", []]
   vs[1].append((False, '\xed\xa0\x80\xed\xb0\x80'))
   vs[1].append((False, '\xed\xa0\x80\xed\xbf\xbf'))
   vs[1].append((False, '\xed\xad\xbf\xed\xb0\x80'))
   vs[1].append((False, '\xed\xad\xbf\xed\xbf\xbf'))
   vs[1].append((False, '\xed\xae\x80\xed\xb0\x80'))
   vs[1].append((False, '\xed\xae\x80\xed\xbf\xbf'))
   vs[1].append((False, '\xed\xaf\xbf\xed\xb0\x80'))
   vs[1].append((False, '\xed\xaf\xbf\xed\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   # 5.3 Other illegal code positions
   # Those are non-character code points and valid UTF-8 by RFC 3629
   vs = ["Non-character code points (valid UTF-8)", []]
   # https://bug686312.bugzilla.mozilla.org/attachment.cgi?id=561257
   # non-characters: EF BF [BE-BF]
   vs[1].append((True, '\xef\xbf\xbe'))
   vs[1].append((True, '\xef\xbf\xbf'))
   # non-characters: F[0-7] [89AB]F BF [BE-BF]
   for z1 in ['\xf0', '\xf1', '\xf2', '\xf3', '\xf4']:
      for z2 in ['\x8f', '\x9f', '\xaf', '\xbf']:
         if not (z1 == '\xf4' and z2 != '\x8f'): # those encode codepoints >U+10FFFF
            for z3 in ['\xbe', '\xbf']:
               zz = z1 + z2 + '\xbf' + z3
               if zz not in ['\xf0\x8f\xbf\xbe', '\xf0\x8f\xbf\xbf']: # filter overlong sequences
                  vs[1].append((True, zz))
   UTF8_TEST_SEQUENCES.append(vs)

   # Unicode "specials", such as replacement char etc
   # http://en.wikipedia.org/wiki/Specials_%28Unicode_block%29
   vs = ["Unicode specials (i.e. replacement char)", []]
   vs[1].append((True, '\xef\xbf\xb9'))
   vs[1].append((True, '\xef\xbf\xba'))
   vs[1].append((True, '\xef\xbf\xbb'))
   vs[1].append((True, '\xef\xbf\xbc'))
   vs[1].append((True, '\xef\xbf\xbd')) # replacement char
   vs[1].append((True, '\xef\xbf\xbe'))
   vs[1].append((True, '\xef\xbf\xbf'))
   UTF8_TEST_SEQUENCES.append(vs)

   return UTF8_TEST_SEQUENCES


def createValidUtf8TestSequences():
   """
   Generate some exotic, but valid UTF8 test strings.
   """
   VALID_UTF8_TEST_SEQUENCES = []
   for test in createUtf8TestSequences():
      valids = [x[1] for x in test[1] if x[0]]
      if len(valids) > 0:
         VALID_UTF8_TEST_SEQUENCES.append([test[0], valids])
   return VALID_UTF8_TEST_SEQUENCES


def test_utf8(validator):
   """
   These tests verify the UTF-8 decoder/validator on the various test cases from
   http://www.cl.cam.ac.uk/~mgk25/ucs/examples/UTF-8-test.txt
   """
   vs = []
   for k in createUtf8TestSequences():
      vs.extend(k[1])

   # All Unicode code points
   for i in xrange(0, 0xffff): # should by 0x10ffff, but non-wide Python build is limited to 16-bits
      if i < 0xD800 or i > 0xDFFF: # filter surrogate code points, which are disallowed to encode in UTF-8
         vs.append((True, unichr(i).encode("utf-8")))

   # 5.1 Single UTF-16 surrogates
   for i in xrange(0xD800, 0xDBFF): # high-surrogate
      ss = unichr(i).encode("utf-8")
      vs.append((False, ss))
   for i in xrange(0xDC00, 0xDFFF): # low-surrogate
      ss = unichr(i).encode("utf-8")
      vs.append((False, ss))

   # 5.2 Paired UTF-16 surrogates
   for i in xrange(0xD800, 0xDBFF): # high-surrogate
      for j in xrange(0xDC00, 0xDFFF): # low-surrogate
         ss1 = unichr(i).encode("utf-8")
         ss2 = unichr(j).encode("utf-8")
         vs.append((False, ss1 + ss2))
         vs.append((False, ss2 + ss1))

   print "testing validator %s on %d UTF8 sequences" % (validator, len(vs))

   # now test and assert ..
   for s in vs:
      validator.reset()
      r = validator.validate(s[1])
      res = r[0] and r[1] # no UTF-8 decode error and everything consumed
      assert res == s[0]

   print "ok, validator works!"
   print


def test_utf8_incremental(validator, withPositions = True):
   """
   These tests verify that the UTF-8 decoder/validator can operate incrementally.
   """
   if withPositions:
      k = 4
      print "testing validator %s on incremental detection with positions" % validator
   else:
      k = 2
      print "testing validator %s on incremental detection without positions" % validator

   validator.reset()
   assert (True, True, 15, 15)[:k] == validator.validate("µ@ßöäüàá")[:k]

   validator.reset()
   assert (False, False, 0, 0)[:k] == validator.validate("\xF5")[:k]

   ## the following 3 all fail on eating byte 7 (0xA0)
   validator.reset()
   assert (True, True, 6, 6)[:k] == validator.validate("\x65\x64\x69\x74\x65\x64")[:k]
   assert (False, False, 1, 7)[:k] == validator.validate("\xED\xA0\x80")[:k]

   validator.reset()
   assert (True, True, 4, 4)[:k] == validator.validate("\x65\x64\x69\x74")[:k]
   assert (False, False, 3, 7)[:k] == validator.validate("\x65\x64\xED\xA0\x80")[:k]

   validator.reset()
   assert (True, False, 7, 7)[:k] == validator.validate("\x65\x64\x69\x74\x65\x64\xED")[:k]
   assert (False, False, 0, 7)[:k] == validator.validate("\xA0\x80")[:k]

   print "ok, validator works!"
   print


Case6_X_X = []
Case6_X_X_CaseSubCategories = {}


def __init__(self, protocol):
   Case.__init__(self, protocol)

def onOpen(self):

   if self.isValid:
      self.expected[Case.OK] = [("message", self.PAYLOAD, False)]
      self.expectedClose = {"closedByMe": True,
                            "closeCode": [self.p.CLOSE_STATUS_CODE_NORMAL],
                            "requireClean": True}
   else:
      self.expected[Case.OK] = []
      self.expectedClose = {"closedByMe": False,
                            "closeCode": [self.p.CLOSE_STATUS_CODE_INVALID_PAYLOAD],
                            "requireClean": False,
                            "closedByWrongEndpointIsFatal": True}

   self.p.sendMessage(self.PAYLOAD, False)
   self.p.killAfter(0.5)


i = 5
for t in createUtf8TestSequences():
   j = 1
   Case6_X_X_CaseSubCategories["6.%d" % i] = t[0]
   for p in t[1]:
      if p[0]:
         desc = "Send a text message with payload which is valid UTF-8 in one fragment."
         exp = "The message is echo'ed back to us."
      else:
         desc = "Send a text message with payload which is not valid UTF-8 in one fragment."
         exp = "The connection is failed immediately, since the payload is not valid UTF-8."
      C = type("Case6_%d_%d" % (i, j),
                (object, Case, ),
                {"PAYLOAD": p[1],
                 "isValid": p[0],
                 "DESCRIPTION": """%s<br><br>Payload: 0x%s""" % (desc, binascii.b2a_hex(p[1])),
                 "EXPECTATION": """%s""" % exp,
                 "__init__": __init__,
                 "onOpen": onOpen})
      Case6_X_X.append(C)
      j += 1
   i += 1


import binascii
import array

def encode(c):
   """
   Encode Unicode code point into UTF-8 byte string.
   """
   if c <= 0x7F:
      b1 = c>>0  & 0x7F | 0x00
      return array.array('B', [b1]).tostring()
   elif c <= 0x07FF:
      b1 = c>>6  & 0x1F | 0xC0
      b2 = c>>0  & 0x3F | 0x80
      return array.array('B', [b1, b2]).tostring()
   elif c <= 0xFFFF:
      b1 = c>>12 & 0x0F | 0xE0
      b2 = c>>6  & 0x3F | 0x80
      b3 = c>>0  & 0x3F | 0x80
      return array.array('B', [b1, b2, b3]).tostring()
   elif c <= 0x1FFFFF:
      b1 = c>>18 & 0x07 | 0xF0
      b2 = c>>12 & 0x3F | 0x80
      b3 = c>>6  & 0x3F | 0x80
      b4 = c>>0  & 0x3F | 0x80
      return array.array('B', [b1, b2, b3, b4]).tostring()
   elif c <= 0x3FFFFFF:
      b1 = c>>24 & 0x03 | 0xF8
      b2 = c>>18 & 0x3F | 0x80
      b3 = c>>12 & 0x3F | 0x80
      b4 = c>>6  & 0x3F | 0x80
      b5 = c>>0  & 0x3F | 0x80
      return array.array('B', [b1, b2, b3, b4, b5]).tostring()
   elif c <= 0x7FFFFFFF:
      b1 = c>>30 & 0x01 | 0xFC
      b2 = c>>24 & 0x3F | 0x80
      b3 = c>>18 & 0x3F | 0x80
      b4 = c>>12 & 0x3F | 0x80
      b5 = c>>6  & 0x3F | 0x80
      b6 = c>>0  & 0x3F | 0x80
      return array.array('B', [b1, b2, b3, b4, b5, b6]).tostring()
   else:
      raise Exception("invalid unicode codepoint")


def test_encode(testpoints):
   """
   Compare Python UTF-8 encoding with adhoc implementation.
   """
   for tp in testpoints:
      if tp[0]:
         print binascii.b2a_hex(encode(tp[0]))
      else:
         print tp[0]
      if tp[1]:
         print binascii.b2a_hex(tp[1].encode("utf8"))
      else:
         print tp[1]


if __name__ == '__main__':
   """
   Run unit tests.
   """

   validator = Utf8Validator()
   test_utf8(validator)
   test_utf8_incremental(validator, withPositions = True)

   #TESTPOINTS = [(0xfffb, u'\ufffb'),
   #              # (0xd807, u'\ud807'), # Jython does not like this
   #              (0x11000, None),
   #              (0x110000, None)]
   #test_encode(TESTPOINTS)

   #from pprint import pprint
   #pprint(createValidUtf8TestSequences())
