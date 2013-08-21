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

import sys, os, json, pkg_resources

from twisted.python import log, usage
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource

import autobahn
import autobahntestsuite

from autobahn.websocket import connectWS, listenWS
from autobahn.utf8validator import Utf8Validator
from autobahn.xormasker import XorMaskerNull

from fuzzing import FuzzingClientFactory, FuzzingServerFactory
from wampfuzzing import FuzzingWampClient
from echo import EchoClientFactory, EchoServerFactory
from broadcast import BroadcastClientFactory, BroadcastServerFactory
from testee import TesteeClientFactory, TesteeServerFactory
from wsperfcontrol import WsPerfControlFactory
from wsperfmaster import WsPerfMasterFactory, WsPerfMasterUiFactory
from wamptestserver import WampTestServerFactory
from massconnect import MassConnectTest


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
            'wampclient',
            'massconnect']

   # Modes that need a specification file
   MODES_NEEDING_SPEC = ['fuzzingclient',
                         'fuzzingserver',
                         'wsperfcontrol',
                         'massconnect']

   # Modes that need a Websocket URI
   MODES_NEEDING_WSURI = ['echoclient',
                          'echoserver',
                          'broadcastclient',
                          'broadcastserver',
                          'testeeclient',
                          'testeeserver',
                          'wsperfcontrol',
                          'wampserver',
                          'wampclient']

   # Default content of specification files for various modes
   DEFAULT_SPECIFICATIONS = {'fuzzingclient':     SPEC_FUZZINGCLIENT,
                             'fuzzingserver':     SPEC_FUZZINGSERVER,
                             'wsperfcontrol':     SPEC_WSPERFCONTROL,
                             'massconnect':       SPEC_MASSCONNECT,
                             'fuzzingwampclient': SPEC_FUZZINGWAMPCLIENT,
                             'fuzzingwampserver': SPEC_FUZZINGWAMPSERVER
                             }

   
   optParameters = [
      ['mode', 'm', None, 'Test mode, one of: %s [required]' % ', '.join(MODES)],
      ['spec', 's', None, 'Test specification file [required in some modes].'],
      ['wsuri', 'w', None, 'WebSocket URI [required in some modes].'],
      ['key', 'k', None, ('Server private key file for secure WebSocket (WSS) '
                          '[required in server modes for WSS].')],
      ['cert', 'c', None, ('Server certificate file for secure WebSocket (WSS) '
                           '[required in server modes for WSS].')],
      ['ident', 'i', None,
       'Override client or server identifier for testee modes.']
   ]

   optFlags = [
      ['debug', 'd', 'Debug output [default: off].'],
      ['autobahnversion', 'a',
       'Print version information for Autobahn and AutobahnTestSuite.']
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
         raise usage.UsageError, "invalid mode %s" % self['mode']

      if self['mode'] in ['fuzzingclient',
                          'fuzzingserver',
                          'fuzzingwampclient',
                          'fuzzingwampserver',
                          'wsperfcontrol',
                          'massconnect']:
         if not self['spec']:
          self.updateSpec()

      if self['mode'] in WsTestOptions.MODES_NEEDING_WSURI and not self['wsuri']:
         raise usage.UsageError, "mode needs a WebSocket URI!"

   def updateSpec(self):
      """
      Update the 'spec' option according to the chosen mode.
      Create a specification file if necessary.
      """

      self['spec'] = filename = "%s.json" % self['mode']
      content = WsTestOptions.DEFAULT_SPECIFICATIONS[self['mode']]

      if not os.path.isfile(filename):
         print "Auto-generating spec file %s" % filename
         f = open(filename, 'w')
         f.write(content)
         f.close()
      else:
         print "Using implicit spec file %s" % filename

# Help string to be presented if the user wants to use an encrypted connection
# but didn't specify key and / or certificate
OPENSSL_HELP = """
Server key and certificate required for WSS
To generate server test key/certificate:

openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 3650 -in server.csr -signkey server.key -out server.crt

Then start wstest:

wstest -m echoserver -w wss://localhost:9000 -k server.key -c server.crt
"""

def createWssContext(o, factory):
   """Create an SSL context factory for WSS connections.
   """

   if factory.isSecure:

      # Check if an OpenSSL library can be imported; abort if it's missing. 
      try:
         from twisted.internet import ssl
      except ImportError, e:
         print "You need OpenSSL/pyOpenSSL installed for secure WebSockets (wss)!"
         sys.exit(1)

      # Make sure the necessary options ('key' and 'cert') are available
      if o.opts['key'] is None or o.opts['cert'] is None:
         print OPENSSL_HELP
         sys.exit(1)

      # Create the context factory based on the given key and certificate
      key = str(o.opts['key'])
      cert = str(o.opts['cert'])
      contextFactory = ssl.DefaultOpenSSLContextFactory(key, cert)

   else:
      contextFactory = None

   return contextFactory


def loadTestData():
   TEST_DATA = {
      'gutenberg_faust':
         {'desc': "Human readable text, Goethe's Faust I (German)",
          'url': 'http://www.gutenberg.org/cache/epub/2229/pg2229.txt',
          'file':
             'pg2229.txt'
          },
      'lena512':
         {'desc': 'Lena Picture, Bitmap 512x512 bw',
          'url': 'http://www.ece.rice.edu/~wakin/images/lena512.bmp',
          'file': 'lena512.bmp'
          },
      'ooms':
         {'desc': 'A larger PDF',
          'url':
             'http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.105.5439',
          'file': '10.1.1.105.5439.pdf'
          },
      'json_data1':
         {'desc': 'Large JSON data file',
          'url': None,
          'file': 'data1.json'
          },
      'html_data1':
         {'desc': 'Large HTML file',
          'url': None,
          'file': 'data1.html'
          }
      }

   for t in TEST_DATA:
      fn = pkg_resources.resource_filename("autobahntestsuite",
                                           "testdata/%s" % TEST_DATA[t]['file'])
      TEST_DATA[t]['data'] = open(fn, 'rb').read()

   return TEST_DATA


def run():

   o = WsTestOptions()
   try:
      o.parseOptions()
   except usage.UsageError, errortext:
      print '%s %s\n' % (sys.argv[0], errortext)
      print 'Try %s --help for usage details\n' % sys.argv[0]
      sys.exit(1)

   debug = o.opts['debug']
   if debug:
      log.startLogging(sys.stdout)

   print "Using Twisted reactor class %s" % str(reactor.__class__)
   print "Using UTF8 Validator class %s" % str(Utf8Validator)
   print "Using XOR Masker classes %s" % str(XorMaskerNull)

   mode = str(o.opts['mode'])

   testData = loadTestData()

   if mode in ['fuzzingclient',
               'fuzzingserver',
               'fuzzingwampclient',
               'fuzzingwampserver']:

      spec = str(o.opts['spec'])
      spec = json.loads(open(spec).read())

      if mode == 'fuzzingserver':

         ## use TLS server key/cert from spec, but allow overriding
         ## from cmd line
         if not o.opts['key']:
            o.opts['key'] = spec.get('key', None)
         if not o.opts['cert']:
            o.opts['cert'] = spec.get('cert', None)

         factory = FuzzingServerFactory(spec, debug)
         factory.testData = testData
         context = createWssContext(o, factory)
         listenWS(factory, context)

         webdir = File(pkg_resources.resource_filename("autobahntestsuite",
                                                       "web/fuzzingserver"))
         curdir = File('.')
         webdir.putChild('cwd', curdir)
         web = Site(webdir)
         if factory.isSecure:
            reactor.listenSSL(spec.get("webport", 8080), web, context)
         else:
            reactor.listenTCP(spec.get("webport", 8080), web)

      elif mode == 'fuzzingclient':
         factory = FuzzingClientFactory(spec, debug)
         factory.testData = testData
         # no connectWS done here, since this is done within
         # FuzzingClientFactory automatically to orchestrate tests

      elif mode == 'fuzzingwampserver':

         raise Exception("not implemented")

      elif mode == 'fuzzingwampclient':

         client = FuzzingWampClient(spec, debug)
         # no connectWS done here, since this is done within
         # FuzzingWampClient automatically to orchestrate tests

      else:
         raise Exception("logic error")

   elif mode in ['testeeclient', 'testeeserver']:

      wsuri = str(o.opts['wsuri'])

      if mode == 'testeeserver':
         factory = TesteeServerFactory(wsuri, debug, ident = o.opts['ident'])
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'testeeclient':
         factory = TesteeClientFactory(wsuri, debug, ident = o.opts['ident'])
         connectWS(factory)

      else:
         raise Exception("logic error")

   elif mode in ['echoclient', 'echoserver']:

      wsuri = str(o.opts['wsuri'])

      if mode == 'echoserver':

         webdir = File(pkg_resources.resource_filename("autobahntestsuite",
                                                       "web/echoserver"))
         web = Site(webdir)
         reactor.listenTCP(8080, web)

         factory = EchoServerFactory(wsuri, debug)
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'echoclient':
         factory = EchoClientFactory(wsuri, debug)
         connectWS(factory)

      else:
         raise Exception("logic error")

   elif mode in ['broadcastclient', 'broadcastserver']:

      wsuri = str(o.opts['wsuri'])

      if mode == 'broadcastserver':

         webdir = File(pkg_resources.resource_filename("autobahntestsuite",
                                                       "web/broadcastserver"))
         web = Site(webdir)
         reactor.listenTCP(8080, web)

         factory = BroadcastServerFactory(wsuri, debug)
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'broadcastclient':
         factory = BroadcastClientFactory(wsuri, debug)
         connectWS(factory)

      else:
         raise Exception("logic error")

   elif mode == 'wsperfcontrol':

      wsuri = str(o.opts['wsuri'])

      spec = str(o.opts['spec'])
      spec = json.loads(open(spec).read())

      factory = WsPerfControlFactory(wsuri)
      factory.spec = spec
      factory.debugWsPerf = spec['options']['debug']

      connectWS(factory)

   elif mode == 'wsperfmaster':

      ## WAMP Server for wsperf slaves
      ##
      wsperf = WsPerfMasterFactory("ws://localhost:9090")
      wsperf.debugWsPerf = False
      listenWS(wsperf)

      ## Web Server for UI static files
      ##
      webdir = File(pkg_resources.resource_filename("autobahntestsuite",
                                                    "web/wsperfmaster"))
      web = Site(webdir)
      reactor.listenTCP(8080, web)

      ## WAMP Server for UI
      ##
      wsperfUi = WsPerfMasterUiFactory("ws://localhost:9091")
      wsperfUi.debug = False
      wsperfUi.debugWamp = False
      listenWS(wsperfUi)

      ## Connect servers
      ##
      wsperf.uiFactory = wsperfUi
      wsperfUi.slaveFactory = wsperf

   elif mode in ['wampclient', 'wampserver']:

      wsuri = str(o.opts['wsuri'])

      if mode == 'wampserver':

         webdir = File(pkg_resources.resource_filename("autobahntestsuite",
                                                       "web/wamp"))
         web = Site(webdir)
         reactor.listenTCP(8080, web)

         factory = WampTestServerFactory(wsuri, debug)
         listenWS(factory, createWssContext(o, factory))

      elif mode == 'wampclient':
         raise Exception("not yet implemented")

      else:
         raise Exception("logic error")

   elif mode == 'massconnect':

      spec = str(o.opts['spec'])
      spec = json.loads(open(spec).read())

      test = MassConnectTest(spec)
      d = test.run()
      def onTestEnd(res):
         print res
         reactor.stop()
      d.addCallback(onTestEnd)

   else:

      raise Exception("logic error")

   reactor.run()


if __name__ == '__main__':
   run()
