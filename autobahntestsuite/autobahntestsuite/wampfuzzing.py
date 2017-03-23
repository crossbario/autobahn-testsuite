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

__all__ = ("FuzzingWampClient",)

from zope.interface import implementer
from zope.interface.verify import verifyObject, verifyClass

from twisted.internet.defer import returnValue, \
                                   inlineCallbacks

import autobahn
import autobahntestsuite

from autobahn.wamp1.protocol import exportRpc, \
                                    WampServerProtocol, \
                                    WampServerFactory

from interfaces import ITestRunner, ITestDb
from rinterfaces import RITestDb, RITestRunner
from testrun import TestRun, Testee



@implementer(ITestRunner)
@implementer(RITestRunner)
class FuzzingWampClient(object):
   """
   A test driver for WAMP test cases.

   The test driver takes a test specification and orchestrates the execution of tests
   against the set of testees (as specified in the test spec).
   """

   MODENAME = 'fuzzingwampclient'


   def __init__(self, testDb, debug = False):

      assert(verifyObject(ITestDb, testDb))
      assert(verifyObject(RITestDb, testDb))

      self._testDb = testDb
      self._debug = debug
      self.dispatch = None


   @exportRpc
   def run(self, specName, saveResults = True):
      return self.runAndObserve(specName, saveResults = saveResults)


   @inlineCallbacks
   def runAndObserve(self, specName, observers_ = [], saveResults = True):

      specId, spec = yield self._testDb.getSpecByName(specName)
      casesByTestee = yield self._testDb.generateCasesByTestee(specId)
      _observers = observers_[:]
      #_observers = observers_

      ## publish WAMP event on test case finished
      ##
      def notify(runId, testRun, testCase, result, remaining):
         if testCase:
            evt = {
               'testee': testRun.testee.name,
               'runId': runId,
               'index': testCase.index,
               'passed': result.passed,
               'remaining': remaining
            }
            topic = "http://api.testsuite.wamp.ws/testrun#onResult"
         else:
            evt = {
               'testee': testRun.testee.name,
               'runId': runId
            }
            topic = "http://api.testsuite.wamp.ws/testrun#onComplete"

         self.dispatch(topic, evt)
         #if result and not result.passed:
         #   print topic, evt

      if self.dispatch:
         _observers.append(notify)

      ## save test results to test database
      ##
      def save(runId, testRun, testCase, result, remaining):
         if testCase:
            self._testDb.saveResult(runId, testRun, testCase, result, saveResults)

      if saveResults:
         _observers.append(save)

      testRuns = []
      for obj in spec['testees']:
         testee = Testee(**obj)
         cases = casesByTestee.get(testee.name, [])
         if testee.options.has_key('randomize') and testee.options['randomize'] is not None:
            randomize = testee.options['randomize']
         elif spec.has_key('options') and spec['options'].has_key('randomize') and spec['options']['randomize'] is not None:
            randomize = spec['options']['randomize']
         else:
            randomize = False
         testRun = TestRun(testee, cases, randomize = randomize)
         testRuns.append(testRun)

      runId = yield self._testDb.newRun(specId)

      print
      print "Autobahn Fuzzing WAMP Client"
      print
      print "Autobahn Version          : %s" % autobahn.version
      print "AutobahnTestsuite Version : %s" % autobahntestsuite.version
      #print "WAMP Test Cases           : %d" % len(self._caseSet.Cases)
      print "WAMP Testees              : %d" % len(spec["testees"])
      print
      for testRun in testRuns:
         print "%s @ %s : %d test cases prepared" % (testRun.testee.name, testRun.testee.url, testRun.remaining())
      print
      print

      def progress(runId, testRun, testCase, result, remaining):
         for obsv in _observers:
            try:
               obsv(runId, testRun, testCase, result, remaining)
            except Exception, e:
               print e

      if spec.get('parallel', False):
         fails, resultIds = yield self._runParallel(runId, spec, testRuns, progress)
      else:
         fails, resultIds = yield self._runSequential(runId, spec, testRuns, progress)

      yield self._testDb.closeRun(runId)

      returnValue((runId, resultIds))


   @inlineCallbacks
   def _runSequential(self, runId, spec, testRuns, progress):
      """
      Execute all test runs sequentially - that is for each
      testee (one after another), run the testee's set of
      test cases sequentially.
      """
      ## we cumulate number of test fails and progress() return values
      ##
      fails = 0
      progressResults = []

      for testRun in testRuns:
         while True:
            ## get next test case _class_ for test run
            ##
            TestCase = testRun.next()

            if TestCase:
               ## run test case, let fire progress() callback and cumulate results
               ##
               try:
                  testCase = TestCase(testRun.testee, spec)
               except Exception, e:
                  print "ERROR 1", e
               else:
                  try:
                     result = yield testCase.run()
                  except Exception, e:
                     print "ERROR 2", e
               if not result.passed:
                  fails += 1
               pres = yield progress(runId, testRun, testCase, result, testRun.remaining())
               progressResults.append(pres)
            else:
               ## signal end of test run by firing progress() one last time ..
               ##
               yield progress(runId, testRun, None, None, 0)
               break

      returnValue((fails, progressResults))


   def _runParallel(self, runId, spec, testRuns, progress):
      """
      Execute all test runs in parallel - that is run
      each testee's set of test cases sequentially
      against that testee, but do so for all testees
      in parallel.
      """
      raise Exception("implement me")


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

   ## serve status stuff from a standard File resource
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

   if self.mode == 'fuzzingwampclient':

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

