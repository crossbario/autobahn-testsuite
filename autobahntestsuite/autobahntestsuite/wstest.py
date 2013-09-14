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

import sys, os, json, pkg_resources, uuid
from pprint import pprint

from twisted.python import log, usage
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred, returnValue
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.web.resource import Resource

from flask import Flask, render_template

import autobahn
import autobahntestsuite

from autobahn.websocket import connectWS, listenWS
from autobahn.utf8validator import Utf8Validator
from autobahn.xormasker import XorMaskerNull
from autobahn.wamp import WampServerFactory
from autobahn.resource import WSGIRootResource

from fuzzing import FuzzingClientFactory, FuzzingServerFactory
from wampfuzzing import FuzzingWampClient
from echo import EchoClientFactory, EchoServerFactory
from broadcast import BroadcastClientFactory, BroadcastServerFactory
from testee import TesteeClientFactory, TesteeServerFactory
from wsperfcontrol import WsPerfControlFactory
from wsperfmaster import WsPerfMasterFactory, WsPerfMasterUiFactory
from wamptestserver import WampTestServerFactory
from wamptestee import TesteeWampServerProtocol
from massconnect import MassConnectTest
from testdb import TestDb
from interfaces import ITestDb
from wampcase import WampCaseSet
from util import Tabify

import jinja2
import klein


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
            'web']

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
                          'wampclient',
                          'wamptesteeserver']

   # Default content of specification files for various modes
   DEFAULT_SPECIFICATIONS = {'fuzzingclient':     SPEC_FUZZINGCLIENT,
                             'fuzzingserver':     SPEC_FUZZINGSERVER,
                             'wsperfcontrol':     SPEC_WSPERFCONTROL,
                             'massconnect':       SPEC_MASSCONNECT,
                             'fuzzingwampclient': SPEC_FUZZINGWAMPCLIENT,
                             'fuzzingwampserver': SPEC_FUZZINGWAMPSERVER
                             }


   optParameters = [
      ['mode', 'm', None, 'Test mode, one of: %s [required]' %
       ', '.join(MODES)],
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
         raise usage.UsageError, (
            "Mode '%s' is invalid.\nAvailable modes:\n\t- %s" % (
               self['mode'], "\n\t- ".join(sorted(WsTestOptions.MODES))))

      if self['mode'] in ['fuzzingclient',
                          'fuzzingserver',
                          'fuzzingwampclient',
                          'fuzzingwampserver',
                          'wsperfcontrol',
                          'massconnect']:
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
      self.testData = self._loadTestData()

      
   def startService(self):
      methodMapping = dict(
         fuzzingclient     = self.startFuzzingService,
         fuzzingserver     = self.startFuzzingService,
         fuzzingwampclient = self.startFuzzingService,
         fuzzingwampserver = self.startFuzzingService,
         testeeclient      = self.startTesteeService,
         testeeserver      = self.startTesteeService,
         echoclient        = self.startEchoService,
         echoserver        = self.startEchoService,
         broadcastclient   = self.startBroadcastingService,
         broadcastserver   = self.startBroadcastingService,
         wsperfcontrol     = self.startWsPerfControl,
         wsperfmaster      = self.startWsPerfMaster,
         wampclient        = self.startWampService,
         wampserver        = self.startWampService,
         wamptesteeserver  = self.startWampService,
         massconnect       = self.startMassConnect,
         web               = self.startWeb
         )
      try:
         methodMapping[self.mode]()
      except KeyError:
         raise Exception("logic error")


   def startWeb(self):

      if self.debug:
         log.startLogging(sys.stdout)

      app = klein.Klein()
      app.debug = self.debug
      app.db = TestDb()
      app.templates = jinja2.Environment(loader = jinja2.FileSystemLoader('autobahntestsuite/templates'))


      @app.route('/')
      @inlineCallbacks
      def page_home(request):
         res = []
         rows = yield app.db.getTestRuns()
         for row in rows:
            obj = {}
            obj['id'] = row[0]
            obj['mode'] = row[1]
            obj['started'] = row[2]
            obj['ended'] = row[3]
            res.append(obj)
         page = app.templates.get_template('index.html')
         returnValue(page.render(testruns = res))


      @app.route('/testrun/<path:runid>')
      @inlineCallbacks
      def page_show_testrun(*args, **kwargs):
         runid = kwargs.get('runid', None)
         res = yield app.db.getTestRunSummary(runid)
         res2 = yield app.db.getTestRunIndex(runid)
         page = app.templates.get_template('testrun.html')
         returnValue(page.render(testees = res, testresults = res2))


      @app.route('/testresult/<path:resultid>')
      @inlineCallbacks
      def page_show_testresult(*args, **kwargs):
         resultid = kwargs.get('resultid', None)
         testresult = yield app.db.getTestResult(resultid)
         testresult.duration = 1000. * (testresult.ended - testresult.started)
         page = app.templates.get_template('testresult.html')
         returnValue(page.render(testresult = testresult))


      @app.route('/home')
      def page_home_deferred_style(request):
         d1 = Deferred()
         db = TestDb()
         d2 = db.getTestRuns()
         def process(result):
            res = []
            for row in result:
               obj = {}
               obj['runId'] = row[0]
               obj['mode'] = row[1]
               obj['started'] = row[2]
               obj['ended'] = row[3]
               res.append(obj)
            d1.callback(json.dumps(res))
         d2.addCallback(process)
         return d1

      ## serve statuc stuff from a standard File resource
      ##
      static = File("autobahntestsuite/static")

      ## we need to wrap stuff, since the Klein Twisted Web resource
      ## does not seem to support putChild()
      ##
      resource = WSGIRootResource(app.resource(), {'static': static})

      ## serve everything from one port
      ##
      reactor.listenTCP(8090, Site(resource), interface = "0.0.0.0")
      reactor.run()

   def startWeb2(self):
      if self.debug:
         log.startLogging(sys.stdout)
      app = Flask(__name__)
      app.debug = self.debug
      app.secret_key = str(uuid.uuid4())

      db = TestDb()

      @app.route('/')
      def page_home():
         #res = yield db.getTestRuns()
         #print res
         return render_template('index.html')

      flaskResource = WSGIResource(reactor, reactor.getThreadPool(), app)
      site = Site(flaskResource)
      reactor.listenTCP(8090, site)

   @inlineCallbacks
   def startFuzzingService(self):
      spec = self._loadSpec()

      if self.mode == 'fuzzingserver':
         ## use TLS server key/cert from spec, but allow overriding
         ## from cmd line
         if not self.options['key']:
            self.options['key'] = spec.get('key', None)
         if not self.options['cert']:
            self.options['cert'] = spec.get('cert', None)

         factory = FuzzingServerFactory(spec, self.debug)
         factory.testData = self.testData
         context = self._createWssContext(factory)
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

      elif self.mode == 'fuzzingclient':
         factory = FuzzingClientFactory(spec, self.debug)
         factory.testData = self.testData
         # no connectWS done here, since this is done within
         # FuzzingClientFactory automatically to orchestrate tests

      elif self.mode == 'fuzzingwampclient':

         testDb = TestDb(spec.get('dbfile', None))

         testSet = WampCaseSet()
         testRunner = FuzzingWampClient(testDb, testSet)
         runId, resultIds = yield testRunner.run(spec)

         print
         print "Tests finished: run ID %s, result IDs %d" % (runId, len(resultIds))
         print

         summary = yield testDb.getTestRunSummary(runId)
         tab = Tabify(['l32', 'r5', 'r5'])
         print
         print tab.tabify(['Testee', 'Pass', 'Fail'])
         print tab.tabify()
         #for t in sorted(summary.keys()):
         for t in summary:
            print tab.tabify([t['name'], t['passed'], t['failed']])
         print

         #for rid in resultIds:
         #   res = yield testDb.getResult(rid)
         #   print r.runId, r.id, r.passed, r.started, r.ended, r.ended - r.started
         #   #pprint(result)

         reactor.stop()

      elif self.mode == 'fuzzingwampserver':
         raise Exception("not implemented")

      else:
         raise Exception("logic error")


   def startTesteeService(self):
      wsuri = str(self.options['wsuri'])

      if self.mode == 'testeeserver':
         factory = TesteeServerFactory(wsuri, self.debug,
                                       ident = self.options['ident'])
         listenWS(factory, self._createWssContext(factory))

      elif self.mode == 'testeeclient':
         factory = TesteeClientFactory(wsuri, self.debug,
                                       ident = self.options['ident'])
         connectWS(factory)

      else:
         raise Exception("logic error")


   def startEchoService(self):
      wsuri = str(self.options['wsuri'])

      if self.mode == 'echoserver':

         self._setupSite("echoserver")

         factory = EchoServerFactory(wsuri, self.debug)
         listenWS(factory, self._createWssContext(factory))

      elif self.mode == 'echoclient':
         factory = EchoClientFactory(wsuri, self.debug)
         connectWS(factory)

      else:
         raise Exception("logic error")


   def startBroadcastingService(self):
      wsuri = str(self.options['wsuri'])

      if self.mode == 'broadcastserver':

         self._setupSite("broadcastserver")

         factory = BroadcastServerFactory(wsuri, self.debug)
         listenWS(factory, self._createWssContext(factory))

      elif self.mode == 'broadcastclient':
         factory = BroadcastClientFactory(wsuri, self.debug)
         connectWS(factory)

      else:
         raise Exception("logic error")


   def startWsPerfControl(self):
      wsuri = str(self.options['wsuri'])
      
      spec = self._loadSpec()
      factory = WsPerfControlFactory(wsuri)
      factory.spec = spec
      factory.debugWsPerf = spec['options']['debug']
      connectWS(factory)


   def startWsPerfMaster(self):
      ## WAMP Server for wsperf slaves
      ##
      wsperf = WsPerfMasterFactory("ws://localhost:9090")
      wsperf.debugWsPerf = False
      listenWS(wsperf)

      ## Web Server for UI static files
      ##
      self._setupSite("wsperfmaster")

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


   def startWampService(self):
      wsuri = str(self.options['wsuri'])

      if self.mode == 'wampserver':

         self._setupSite("wamp")

         factory = WampTestServerFactory(wsuri, self.debug)
         listenWS(factory, self._createWssContext(factory))

      elif self.mode == 'wampclient':
         raise Exception("not yet implemented")

      elif self.mode == 'wamptesteeserver':
         factory = WampServerFactory(wsuri, self.debug)
         factory.protocol = TesteeWampServerProtocol
         listenWS(factory, self._createWssContext(factory))

      else:
         raise Exception("logic error")


   def startMassConnect(self):
      spec = self._loadSpec()

      test = MassConnectTest(spec)
      d = test.run()

      def onTestEnd(res):
         print res
         reactor.stop()

      d.addCallback(onTestEnd)

   ## Helper methods

   def _loadSpec(self):
      spec_filename = os.path.abspath(self.options['spec'])
      print "Loading spec from %s" % spec_filename
      spec = json.loads(open(spec_filename).read())
      return spec

   
   def _setupSite(self, prefix):
      webdir = File(pkg_resources.resource_filename("autobahntestsuite",
                                                    "web/%s" % prefix))
      web = Site(webdir)
      reactor.listenTCP(8080, web)


   def _createWssContext(self, factory):
      """Create an SSL context factory for WSS connections.
      """

      if not factory.isSecure:
         return None

      # Check if an OpenSSL library can be imported; abort if it's missing.
      try:
         from twisted.internet import ssl
      except ImportError, e:
         print ("You need OpenSSL/pyOpenSSL installed for secure WebSockets"
                "(wss)!")
         sys.exit(1)

      # Make sure the necessary options ('key' and 'cert') are available
      if self.options['key'] is None or self.options['cert'] is None:
         print OPENSSL_HELP
         sys.exit(1)

      # Create the context factory based on the given key and certificate
      key = str(self.options['key'])
      cert = str(self.options['cert'])
      return ssl.DefaultOpenSSLContextFactory(key, cert)

   
   def _loadTestData(self):
      test_data = {
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

      for t in test_data:
         fn = pkg_resources.resource_filename("autobahntestsuite",
                                              "testdata/%s" %
                                              test_data[t]['file'])
         test_data[t]['data'] = open(fn, 'rb').read()

      return test_data


def run():
   wstest = WsTestRunner()
   wstest.startService()
   reactor.run()
   

if __name__ == '__main__':
   run()
