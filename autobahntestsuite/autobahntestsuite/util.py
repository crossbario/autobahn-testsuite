###############################################################################
##
##  Copyright 2013 Tavendo GmbH
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

__all__ = ("AttributeBag", "Tabify", "perf_counter", )


import json

from twisted.python import log


# http://docs.python.org/dev/library/time.html#time.perf_counter
# http://www.python.org/dev/peps/pep-0418/
# until time.perf_counter becomes available in Python 2 we do:
import time
if not hasattr(time, 'perf_counter'):
   import os
   if os.name == 'nt':
      perf_counter = time.clock
   else:
      perf_counter = time.time
else:
   perf_counter = time.perf_counter


class AttributeBag:

   def __init__(self, **args):

      for attr in self.ATTRIBUTES:
         setattr(self, attr, None)

      self.set(args)


   def serialize(self):
      obj = {}
      for attr in self.ATTRIBUTES:
         obj[attr] = getattr(self, attr)
      return json.dumps(obj)


   def deserialize(self, data):
      obj = json.loads(data)
      self.set(obj)


   def set(self, obj):
      for attr in obj.keys():
         if attr in self.ATTRIBUTES:
            setattr(self, attr, obj[attr])
         else:
            if self.debug:
               log.msg("Warning: skipping unknown attribute '%s'" % attr)


   def __repr__(self):
      s = []
      for attr in self.ATTRIBUTES:
         s.append("%s = %s" % (attr, getattr(self, attr)))
      return self.__class__.__name__ + '(' + ', '.join(s) + ')'


class Tabify:

   def __init__(self, formats, truncate = 120, filler = ['-', '+']):
      self._formats = formats
      self._truncate = truncate
      self._filler = filler


   def tabify(self, fields = None):
      """
      Tabified output formatting.
      """

      ## compute total length of all fields
      ##
      totalLen = 0
      flexIndicators = 0
      flexIndicatorIndex = None
      for i in xrange(len(self._formats)):
         ffmt = self._formats[i][1:]
         if ffmt != "*":
            totalLen += int(ffmt)
         else:
            flexIndicators += 1
            flexIndicatorIndex = i

      if flexIndicators > 1:
         raise Exception("more than 1 flex field indicator")

      ## reserve space for column separators (" | " or " + ")
      ##
      totalLen += 3 * (len(self._formats) - 1)

      if totalLen > self._truncate:
         raise Exception("cannot fit content in truncate length %d" % self._truncate)

      r = []
      for i in xrange(len(self._formats)):

         if i == flexIndicatorIndex:
            N = self._truncate - totalLen
         else:
            N = int(self._formats[i][1:]) 

         if fields:
            s = str(fields[i])
            if len(s) > N:
               s = s[:N-2] + ".."
            l = N - len(s)
            m = self._formats[i][0]
         else:
            s = ''
            l = N
            m = '+'

         if m == 'l':
            r.append(s + ' ' * l)
         elif m == 'r':
            r.append(' ' * l + s)
         elif m == 'c':
            c1 = l / 2
            c2 = l - c1
            r.append(' ' * c1 + s + ' ' * c2)
         elif m == '+':
            r.append(self._filler[0] * l)
         else:
            raise Exception("invalid field format")

      if m == '+':
         return (self._filler[0] + self._filler[1] + self._filler[0]).join(r)
      else:
         return ' | '.join(r)
