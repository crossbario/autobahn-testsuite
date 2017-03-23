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

from __future__ import absolute_import

__all__ = ['start']

import json
import binascii
from autobahn import wamp
from autobahn.wamp.test.test_serializer import generate_test_messages


def start(outfilename, debug = False):
   with open(outfilename, 'wb') as outfile:
      ser_json = wamp.serializer.JsonSerializer()
      ser_msgpack = wamp.serializer.MsgPackSerializer()

      res = []
      for msg in generate_test_messages():
         case = {}
         case['name'] = str(msg)
         case['rmsg'] = msg.marshal()

         ## serialize message to JSON
         bytes, binary = ser_json.serialize(msg)
         case['json'] = bytes

         ## serialize message to MsgPack
         bytes, binary = ser_msgpack.serialize(msg)
         case['msgpack'] = binascii.hexlify(bytes)

         res.append(case)

      outfile.write(json.dumps(res, indent = 3))
