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

## don't touch: must be first import!
import choosereactor

import os, json, sys, pkg_resources

from twisted.internet import reactor
from twisted.python import log, usage
from twisted.internet.defer import Deferred


## for versions
import autobahn
import autobahntestsuite
from autobahn.websocket.utf8validator import Utf8Validator
from autobahn.websocket.xormasker import XorMaskerNull

## WebSocket testing modes
import testee
import fuzzing

## WAMP testing modes
#import wamptestee
#import wampfuzzing

## Misc testing modes
import echo
import broadcast
import massconnect
#import wsperfcontrol
#import wsperfmaster
import serializer


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
            #'fuzzingwampserver',
            #'fuzzingwampclient',
            'testeeserver',
            'testeeclient',
            #'wsperfcontrol',
            #'wsperfmaster',
            #'wampserver',
            #'wamptesteeserver',
            #'wampclient',
            'massconnect',
            #'web',
            #'import',
            #'export',
            'serializer'
            ]

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
      ['outfile', 'o', None, 'Output filename for modes that generate testdata.'],
      ['wsuri', 'w', None, 'WebSocket URI [required in some modes].'],
      ['webport', 'u', 8080, 'Web port for running an embedded HTTP Web server; defaults to 8080; set to 0 to disable. [optionally used in some modes: fuzzingserver, echoserver, broadcastserver, wsperfmaster].'],
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

      if (self['mode'] in WsTestOptions.MODES_NEEDING_WSURI and not self['wsuri']):
         raise usage.UsageError, "mode needs a WebSocket URI!"

      if self['webport'] is not None:
         try:
            self['webport'] = int(self['webport'])
            if self['webport'] < 0 or self['webport'] > 65535:
               raise ValueError()
         except:
            raise usage.UsageError, "invalid Web port %s" % self['webport']



class WsTestRunner(object):
   """
   Testsuite driver.
   """

   def __init__(self, options, spec = None):
      self.options = options
      self.spec = spec

      self.debug = self.options.get('debug', False)
      if self.debug:
         log.startLogging(sys.stdout)

      self.mode = str(self.options['mode'])


   def startService(self):
      """
      Start mode specific services.
      """
      print
      print "Using Twisted reactor class %s" % str(reactor.__class__)
      print "Using UTF8 Validator class %s" % str(Utf8Validator)
      print "Using XOR Masker classes %s" % str(XorMaskerNull)
      #print "Using JSON processor module '%s'" % str(autobahn.wamp.json_lib.__name__)
      print

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
         return broadcast.startServer(self.options['wsuri'], self.options['webport'], debug = self.debug)

      elif self.mode == "echoclient":
         return echo.startClient(self.options['wsuri'], debug = self.debug)

      elif self.mode == "echoserver":
         return echo.startServer(self.options['wsuri'], self.options['webport'], debug = self.debug)

      elif self.mode == "fuzzingclient":
         # allow overriding servers from command line option, providing 1 server
         # this is semi-useful, as you cannot accumulate a combined report for
         # multiple servers by running wstest over and over again. the generated
         # report is only for the last invocation - it would require a massive
         # code restructering / rewriting to change that. no time for that unfort.
         servers = self.spec.get("servers", [])
         if len(servers) == 0:
             self.spec["servers"] = [{"url": self.options['wsuri']}]
         return fuzzing.startClient(self.spec, debug = self.debug)

      elif self.mode == "fuzzingserver":
         return fuzzing.startServer(self.spec, self.options['webport'], debug = self.debug)

      elif self.mode == "wsperfcontrol":
         return wsperfcontrol.startClient(self.options['wsuri'], self.spec, debug = self.debug)

      elif self.mode == "wsperfmaster":
         return wsperfmaster.startServer(self.options['webport'], debug = self.debug)

      elif self.mode == "massconnect":
         return massconnect.startClient(self.spec, debug = self.debug)

      elif self.mode == "serializer":
         return serializer.start(outfilename = self.options['outfile'], debug = self.debug)

      else:
         raise Exception("no mode '%s'" % self.mode)



def start(options, spec = None):
   """
   Actually startup a wstest run.

   :param options: Global options controlling wstest.
   :type options: dict
   :param spec: Test specification needed for certain modes. If none is given, but
                a spec is needed, a default spec is used.
   :type spec: dict
   """
   if options['mode'] in WsTestOptions.MODES_NEEDING_SPEC and spec is None:
      spec = json.loads(WsTestOptions.DEFAULT_SPECIFICATIONS[options['mode']])

   wstest = WsTestRunner(options, spec)
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



def run():
   """
   Run wstest from command line. This parses command line args etc.
   """

   ## parse wstest command lines options
   ##
   cmdOpts = WsTestOptions()
   try:
      cmdOpts.parseOptions()
   except usage.UsageError, errortext:
      print '%s %s\n' % (sys.argv[0], errortext)
      print 'Try %s --help for usage details\n' % sys.argv[0]
      sys.exit(1)
   else:
      options = cmdOpts.opts

   ## check if mode needs a spec ..
   ##
   if options['mode'] in WsTestOptions.MODES_NEEDING_SPEC:

      ## .. if none was given ..
      ##
      if not options['spec']:

         ## .. assume canonical specfile name ..
         ##
         filename = "%s.json" % options['mode']
         options['spec'] = filename

         if not os.path.isfile(filename):

            ## .. if file does not exist, autocreate a spec file
            ##
            content = WsTestOptions.DEFAULT_SPECIFICATIONS[options['mode']]
            print "Auto-generating spec file '%s'" % filename
            f = open(filename, 'w')
            f.write(content)
            f.close()
         else:
            ## .. use existing one
            ##
            print "Using implicit spec file '%s'" % filename

      else:
         ## use explicitly given specfile
         ##
         print "Using explicit spec file '%s'" % options['spec']

      ## now load the spec ..
      ##
      spec_filename = os.path.abspath(options['spec'])
      print "Loading spec from %s" % spec_filename
      spec = json.loads(open(spec_filename).read())

   else:
      ## mode does not rely on spec
      ##
      spec = None

   ## now start a wstest run ..
   ##
   start(options, spec)



if __name__ == '__main__':
   run()
