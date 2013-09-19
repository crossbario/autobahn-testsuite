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
from datetime import datetime
from pprint import pprint

from zope.interface.verify import verifyObject, verifyClass

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

from autobahn.wamp import exportRpc, \
                          WampServerFactory, \
                          WampServerProtocol

from autobahn.resource import WSGIRootResource, WebSocketResource
from autobahn.util import parseutc

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
from interfaces import ITestDb, ITestRunner
from wampcase import WampCaseSet
from util import Tabify, envinfo, pprint_timeago

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
      ['key', 'k', None, ('Server private key file for secure WebSocket (WSS) ' '[required in server modes for WSS].')],
      ['cert', 'c', None, ('Server certificate file for secure WebSocket (WSS) ' '[required in server modes for WSS].')],
      ['ident', 'i', None, 'Override client or server identifier for testee modes.']
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

class WsTestWampProtocol(WampServerProtocol):

   def onSessionOpen(self):
      self.registerForPubSub("http://api.testsuite.wamp.ws", True)
      self.registerForRpc(self.factory._testDb, "http://api.testsuite.wamp.ws/testdb/")
      self.registerForRpc(self.factory._testRunner, "http://api.testsuite.wamp.ws/testrunner/")


class WsTestWampFactory(WampServerFactory):

   protocol = WsTestWampProtocol

   def __init__(self, testDb, testRunner, url, debug = False):
      assert(verifyObject(ITestDb, testDb))
      assert(verifyObject(ITestRunner, testRunner))
      WampServerFactory.__init__(self, url, debug = True, debugWamp = True)
      self._testDb = testDb
      self._testRunner = testRunner



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

      try:

         if self.mode == "import":
            return self.startImportSpec(self.options['spec'])

         elif self.mode == "export":
            return self.startExportSpec(self.options['testset'], self.options.get('spec', None))

         elif self.mode == "fuzzingwampclient":
            return self.startFuzzingWampClient(self.options['testset'])

         elif self.mode == "web":
            return self.startWeb(debug = self.debug)

         else:
            pass
      except Exception, e:
         print e
         reactor.stop()


      methodMapping = {
         'fuzzingclient'     : self.startFuzzingService,
         'fuzzingserver'     : self.startFuzzingService,
         'fuzzingwampclient' : self.startFuzzingService,
         'fuzzingwampserver' : self.startFuzzingService,
         'testeeclient'      : self.startTesteeService,
         'testeeserver'      : self.startTesteeService,
         'echoclient'        : self.startEchoService,
         'echoserver'        : self.startEchoService,
         'broadcastclient'   : self.startBroadcastingService,
         'broadcastserver'   : self.startBroadcastingService,
         'wsperfcontrol'     : self.startWsPerfControl,
         'wsperfmaster'      : self.startWsPerfMaster,
         'wampclient'        : self.startWampService,
         'wampserver'        : self.startWampService,
         'wamptesteeserver'  : self.startWampService,
         'massconnect'       : self.startMassConnect,
         'web'               : self.startWeb,
         'import'            : self.startImportSpec,
         'export'            : self.startExportSpec
         }

      return methodMapping[self.mode]()


   @inlineCallbacks
   def startFuzzingWampClient(self, specName):
      """
      Start a WAMP fuzzing client test run using a spec previously imported.
      """
      testSet = WampCaseSet()
      testDb = TestDb([testSet])
      testRunner = FuzzingWampClient(testDb)

      def progress(runId, testRun, testCase, result, remaining):
         if testCase:
            print "%s - %s %s (%d tests remaining)" % (testRun.testee.name, "PASSED   : " if result.passed else "FAILED  : ", testCase.__class__.__name__, remaining)
         else:
            print "FINISHED : Test run for testee '%s' ended." % testRun.testee.name

      runId, resultIds = yield testRunner.runAndObserve(specName, [progress])

      print
      print "Tests finished: run ID %s, result IDs %d" % (runId, len(resultIds))
      print

      summary = yield testDb.getTestRunSummary(runId)

      tab = Tabify(['l32', 'r5', 'r5'])
      print
      print tab.tabify(['Testee', 'Pass', 'Fail'])
      print tab.tabify()
      for t in summary:
         print tab.tabify([t['name'], t['passed'], t['failed']])
      print


   def startImportSpec(self, specFilename):
      """
      Import a test specification into the test database.
      """
      specFilename = os.path.abspath(specFilename)
      print "Importing spec from %s ..." % specFilename
      try:
         spec = json.loads(open(specFilename).read())
      except Exception, e:
         raise Exception("Error: invalid JSON data - %s" % e)

      ## FIXME: this should allow to import not only WAMP test specs,
      ## but WebSocket test specs as well ..
      testSet = WampCaseSet()
      db = TestDb([testSet])

      def done(res):
         op, id, name = res
         if op is None:
            print "Spec under name '%s' already imported and unchanged (Object ID %s)." % (name, id)
         elif op == 'U':
            print "Updated spec under name '%s' (Object ID %s)." % (name, id)
         elif op == 'I':
            print "Imported spec under new name '%s' (Object ID %s)." % (name, id)
         print

      def failed(failure):
         print "Error: spec import failed - %s." % failure.value

      d = db.importSpec(spec)
      d.addCallbacks(done, failed)
      return d


   def startExportSpec(self, specName, specFilename = None):
      """
      Export a (currently active, if any) test specification from the test database by name.
      """
      if specFilename:
         specFilename = os.path.abspath(specFilename)
         fout = open(specFilename, 'w')
      else:
         fout = sys.stdout

      testSet = WampCaseSet()
      db = TestDb([testSet])

      def done(res):
         id, spec = res
         data = json.dumps(spec, sort_keys = True, indent = 3, separators = (',', ': '))
         fout.write(data)
         fout.write('\n')
         if specFilename:
            print "Exported spec '%s' to %s." % (specName, specFilename)
            print

      def failed(failure):
         print "Error: spec export failed - %s" % failure.value
         print

      d = db.getSpecByName(specName)
      d.addCallbacks(done, failed)
      return d


   def startWeb(self, port = 7070, debug = False):
      """
      Start Web service for test database.
      """
      app = klein.Klein()
      app.debug = debug
      app.templates = jinja2.Environment(loader = jinja2.FileSystemLoader('autobahntestsuite/templates'))

      app.db = TestDb([WampCaseSet()], debug = debug)
      app.runner = FuzzingWampClient(app.db, debug = debug)


      @app.route('/')
      @inlineCallbacks
      def page_home(request):
         testruns = yield app.db.getTestRuns(limit = 20)
         rm = {'fuzzingwampclient': 'WAMP/client'}
         cs = {'wamp': 'WAMP'}
         for tr in testruns:
            started = parseutc(tr['started'])
            ended = parseutc(tr['ended'])
            endedOrNow = ended if ended else datetime.utcnow()
            duration = (endedOrNow - started).seconds
            tr['duration'] = duration

            if started:
               tr['started'] = pprint_timeago(started)
            if ended:
               tr['ended'] = pprint_timeago(ended)

            if tr['total']:
               tr['failed'] = tr['total'] - tr['passed']
            else:
               tr['failed'] = 0

            tr['runMode'] = rm[tr['runMode']]
            tr['caseSetName'] = cs[tr['caseSetName']]
         page = app.templates.get_template('index.html')
         returnValue(page.render(testruns = testruns))


      @app.route('/testrun/<path:runid>')
      @inlineCallbacks
      def page_show_testrun(*args, **kwargs):
         runid = kwargs.get('runid', None)
         testees = yield app.db.getTestRunSummary(runid)
         testresults = yield app.db.getTestRunIndex(runid)
         for tr in testresults:
            tr['index'] = "Case " + '.'.join(str(x) for x in tr['index'][0:4])
            for r in tr['results']:
               tr['results'][r]['duration'] *= 1000

         page = app.templates.get_template('testrun.html')
         returnValue(page.render(testees = testees, testresults = testresults))


      @app.route('/testresult/<path:resultid>')
      @inlineCallbacks
      def page_show_testresult(*args, **kwargs):
         resultid = kwargs.get('resultid', None)
         testresult = yield app.db.getTestResult(resultid)

         n = 0
         for k in testresult.expected:
            n += len(testresult.expected[k])
         if n == 0:
            testresult.expected = None

         n = 0
         for k in testresult.observed:
            n += len(testresult.observed[k])
         if n == 0:
            testresult.observed = None

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
      static_resource = File("autobahntestsuite/static")

      ## serve a WAMP server to access the testsuite
      wamp_factory = WsTestWampFactory(app.db, app.runner, "ws://localhost:%d" % port, debug = debug)

      ## we MUST start the factory manually here .. Twisted Web won't
      ## do for us.
      wamp_factory.startFactory()

      ## wire up "dispatch" so that test db/runner can notify
      app.db.dispatch = wamp_factory.dispatch
      app.runner.dispatch = wamp_factory.dispatch

      ## wrap in a Twisted Web resource
      wamp_resource = WebSocketResource(wamp_factory)

      ## we need to wrap our resources, since the Klein Twisted Web resource
      ## does not seem to support putChild(), and we want to have a WebSocket
      ## resource under path "/ws" and our static file serving under "/static"
      root_resource = WSGIRootResource(app.resource(),
         {
            'static': static_resource,
            'ws': wamp_resource
         }
      )

      ## serve everything from one port
      reactor.listenTCP(port, Site(root_resource), interface = "0.0.0.0")

      return True




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

         testSet = WampCaseSet()
         testDb = TestDb([testSet])
         testRunner = FuzzingWampClient(testDb)

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

      return True


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
   res = wstest.startService()
   if res:
      if isinstance(res, Deferred):
         def shutdown(_):
            reactor.stop()
         res.addBoth(shutdown)
      reactor.run()



if __name__ == '__main__':
   run()
