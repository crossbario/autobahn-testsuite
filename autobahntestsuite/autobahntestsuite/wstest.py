###############################################################################
##
##  Copyright 2011-2013 Tavendo GmbH
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

## don't touch: must be first import!
import choosereactor

import os, json, sys, pkg_resources

from twisted.internet import reactor
from twisted.python import log, usage
from twisted.internet.defer import Deferred


## for versions
import autobahn
import autobahntestsuite
from autobahn.utf8validator import Utf8Validator
from autobahn.xormasker import XorMaskerNull

## WebSocket testing modes
import testee
import fuzzing

## WAMP testing modes
import wamptestee
import wampfuzzing

## Misc testing modes
import echo
import broadcast
import massconnect
import wsperfcontrol
import wsperfmaster


from spectemplate import SPEC_FUZZINGSERVER, \
                         SPEC_FUZZINGCLIENT, \
                         SPEC_FUZZINGWAMPSERVER, \
                         SPEC_FUZZINGWAMPCLIENT, \
                         SPEC_WSPERFCONTROL, \
                         SPEC_MASSCONNECT



class WsTestOptions(usage.Options):
   """
   Reads options from the command-line and checks them for plausibility.
   """

   # Available modes, specified with the --mode (or short: -m) flag.
   MODES = ['echoserver',
            'echoclient',
            'broadcastclient',
            'broadcastserver',
            'fuzzingserver',
            'fuzzingclient',
            'fuzzingwampserver',
            'fuzzingwampclient',
            'testeeserver',
            'testeeclient',
            'wsperfcontrol',
            'wsperfmaster',
            'wampserver',
            'wamptesteeserver',
            'wampclient',
            'massconnect',
            'web',
            'import',
            'export']

   # Modes that need a specification file
   MODES_NEEDING_SPEC = ['fuzzingclient',
                         'fuzzingserver',
                         'fuzzingwampserver',
                         'fuzzingwampclient',
                         'wsperfcontrol',
                         'massconnect',
                         'import']

   # Modes that need a Websocket URI
   MODES_NEEDING_WSURI = ['echoclient',
                          'echoserver',
                          'broadcastclient',
                          'broadcastserver',
                          'testeeclient',
                          'testeeserver',
                          'wsperfcontrol',
                          'wampserver',
                          'wampclient',
                          'wamptesteeserver']

   # Default content of specification files for various modes
   DEFAULT_SPECIFICATIONS = {'fuzzingclient':     SPEC_FUZZINGCLIENT,
                             'fuzzingserver':     SPEC_FUZZINGSERVER,
                             'wsperfcontrol':     SPEC_WSPERFCONTROL,
                             'massconnect':       SPEC_MASSCONNECT,
                             'fuzzingwampclient': SPEC_FUZZINGWAMPCLIENT,
                             'fuzzingwampserver': SPEC_FUZZINGWAMPSERVER}

   optParameters = [
      ['mode', 'm', None, 'Test mode, one of: %s [required]' % ', '.join(MODES)],
      ['testset', 't', None, 'Run a test set from an import test spec.'],
      ['spec', 's', None, 'Test specification file [required in some modes].'],
      ['wsuri', 'w', None, 'WebSocket URI [required in some modes].'],
      ['ident', 'i', None, ('Testee client identifier [optional for client testees].')],
      ['key', 'k', None, ('Server private key file for secure WebSocket (WSS) [required in server modes for WSS].')],
      ['cert', 'c', None, ('Server certificate file for secure WebSocket (WSS) [required in server modes for WSS].')]
   ]

   optFlags = [
      ['debug', 'd', 'Debug output [default: off].'],
      ['autobahnversion', 'a', 'Print version information for Autobahn and AutobahnTestSuite.']
   ]

   def postOptions(self):
      """
      Process the given options. Perform plausibility checks, etc...
      """

      if self['autobahnversion']:
         print "Autobahn %s" % autobahn.version
         print "AutobahnTestSuite %s" % autobahntestsuite.version
         sys.exit(0)

      if not self['mode']:
         raise usage.UsageError, "a mode must be specified to run!"

      if self['mode'] not in WsTestOptions.MODES:
         raise usage.UsageError, (
            "Mode '%s' is invalid.\nAvailable modes:\n\t- %s" % (
               self['mode'], "\n\t- ".join(sorted(WsTestOptions.MODES))))

      if self['mode'] in WsTestOptions.MODES_NEEDING_SPEC:
         if not self['spec']:
            self.updateSpec()

      if (self['mode'] in WsTestOptions.MODES_NEEDING_WSURI and
          not self['wsuri']):
         raise usage.UsageError, "mode needs a WebSocket URI!"

   def updateSpec(self):
      """
      Update the 'spec' option according to the chosen mode.
      Create a specification file if necessary.
      """
      self['spec'] = filename = "%s.json" % self['mode']
      content = WsTestOptions.DEFAULT_SPECIFICATIONS[self['mode']]

      if not os.path.isfile(filename):
         print "Auto-generating spec file '%s'" % filename
         f = open(filename, 'w')
         f.write(content)
         f.close()
      else:
         print "Using implicit spec file '%s'" % filename



class WsTestRunner(object):

   def __init__(self):

      print
      print "Using Twisted reactor class %s" % str(reactor.__class__)
      print "Using UTF8 Validator class %s" % str(Utf8Validator)
      print "Using XOR Masker classes %s" % str(XorMaskerNull)
      print "Using JSON processor module '%s'" % str(autobahn.wamp.json_lib.__name__)
      print

      ws_test_options = WsTestOptions()
      try:
         ws_test_options.parseOptions()
      except usage.UsageError, errortext:
         print '%s %s\n' % (sys.argv[0], errortext)
         print 'Try %s --help for usage details\n' % sys.argv[0]
         sys.exit(1)

      self.options = ws_test_options.opts

      self.debug = self.options['debug']
      if self.debug:
         log.startLogging(sys.stdout)

      self.mode = str(self.options['mode'])


   def startService(self):
      """
      Start mode specific services.
      """

      if self.mode == "import":
         return self.startImportSpec(self.options['spec'])

      elif self.mode == "export":
         return self.startExportSpec(self.options['testset'], self.options.get('spec', None))

      elif self.mode == "fuzzingwampclient":
         return self.startFuzzingWampClient(self.options['testset'])

      elif self.mode == "web":
         return self.startWeb(debug = self.debug)

      elif self.mode == "testeeclient":
         return testee.startClient(self.options['wsuri'], ident = self.options['ident'], debug = self.debug)

      elif self.mode == "testeeserver":
         return testee.startServer(self.options['wsuri'], debug = self.debug)

      elif self.mode == "broadcastclient":
         return broadcast.startClient(self.options['wsuri'], debug = self.debug)

      elif self.mode == "broadcastserver":
         return broadcast.startServer(self.options['wsuri'], debug = self.debug)

      elif self.mode == "echoclient":
         return echo.startClient(self.options['wsuri'], debug = self.debug)

      elif self.mode == "echoserver":
         return echo.startServer(self.options['wsuri'], debug = self.debug)

      elif self.mode == "fuzzingclient":
         spec = self._loadSpec()
         return fuzzing.startClient(spec, debug = self.debug)

      elif self.mode == "fuzzingserver":
         spec = self._loadSpec()
         return fuzzing.startServer(spec, debug = self.debug)

      elif self.mode == "wsperfcontrol":
         spec = self._loadSpec()
         return wsperfcontrol.startClient(self.options['wsuri'], spec, debug = self.debug)

      elif self.mode == "wsperfmaster":
         return wsperfmaster.startServer(debug = self.debug)

      elif self.mode == "massconnect":
         spec = self._loadSpec()
         return massconnect.startClient(spec, debug = self.debug)

      else:
         raise Exception("no mode '%s'" % self.mode)


   def _loadSpec(self):
      spec_filename = os.path.abspath(self.options['spec'])
      print "Loading spec from %s" % spec_filename
      spec = json.loads(open(spec_filename).read())
      return spec



def run():
   wstest = WsTestRunner()
   res = wstest.startService()

   ## only start reactor for modes needing it
   ##
   if res:
      ## if mode wants to shutdown reactor after done (e.g. clients),
      ## hook up machinery to do so
      ##
      if isinstance(res, Deferred):
         def shutdown(_):
            reactor.stop()
         res.addBoth(shutdown)
      reactor.run()



if __name__ == '__main__':
   run()
