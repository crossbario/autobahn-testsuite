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

__all__ = ("TestDb",)

import os, sys
import types
import sqlite3
import json

from zope.interface import implementer

from twisted.python import log
from twisted.enterprise import adbapi
from twisted.internet.defer import Deferred

from autobahn.util import utcnow, newid

from interfaces import ITestDb
from testrun import TestResult
from util import envinfo



@implementer(ITestDb)
class TestDb:
   """
   sqlite3 based test database implementing ITestDb. Usually, a single
   instance exists application wide (singleton). Test runners store their
   test results in the database and report generators fetch test results
   from the database. This allows to decouple application parts.
   """

   def __init__(self, caseSets, dbfile = None):

      if not dbfile:
         dbfile = ".wstest.db"

      self._dbfile = os.path.abspath(dbfile)
      if not os.path.isfile(self._dbfile):
         self._createDb()
      else:
         self._checkDb()

      self._dbpool = adbapi.ConnectionPool('sqlite3',
                                           self._dbfile,
                                           check_same_thread = False # http://twistedmatrix.com/trac/ticket/3629
                                          )

      self._caseSets = caseSets
      self._initCaseSets()


   def _initCaseSets(self):
      self._cs = {}
      for cs in self._caseSets:
         if not self._cs.has_key(cs.CaseSetName):
            self._cs[cs.CaseSetName] = {}
         else:
            raise Exception("duplicate case set name")
         for c in cs.Cases:
            idx = tuple(c.index)
            if not self._cs[cs.CaseSetName].has_key(idx):
               self._cs[cs.CaseSetName][idx] = c
            else:
               raise Exception("duplicate case index")

# casesetname -> [{header: {}, children: [{header: {}, children: []}]}]

   def getTestCase(self, caseSetName, caseIndex):
      if self._cs.has_key(caseSetName):
         if self._cs[caseSetName].has_key(caseIndex):
            return self._cs[caseSetName][caseIndex]
      return None


   def getTestCaseIndices(self, caseSetName):
      if self._cs.has_key(caseSetName):
         return sorted(self._cs[caseSetName].keys())
      else:
         return None


   def _createDb(self):
      log.msg("creating test database at %s .." % self._dbfile)
      db = sqlite3.connect(self._dbfile)
      cur = db.cursor()

      cur.execute("""
                  CREATE TABLE testspec (
                     id                TEXT     PRIMARY KEY,
                     before_id         TEXT,
                     valid_from        TEXT     NOT NULL,
                     valid_to          TEXT,
                     name              TEXT     NOT NULL,
                     desc              TEXT,
                     mode              TEXT     NOT NULL,
                     caseset           TEXT     NOT NULL,
                     spec              TEXT     NOT NULL)
                  """)

      cur.execute("""
                  CREATE UNIQUE INDEX
                     idx_testspec_name_valid_to
                        ON testspec (name, valid_to)
                  """)

      cur.execute("""
                  CREATE TABLE testrun (
                     id                TEXT     PRIMARY KEY,
                     testspec_id       TEXT     NOT NULL,
                     env               TEXT     NOT NULL,
                     started           TEXT     NOT NULL,
                     ended             TEXT)
                  """)

      cur.execute("""
                  CREATE TABLE testresult (
                     id                TEXT     PRIMARY KEY,
                     testrun_id        TEXT     NOT NULL,
                     inserted          TEXT     NOT NULL,
                     testee            TEXT     NOT NULL,
                     c1                INTEGER  NOT NULL,
                     c2                INTEGER  NOT NULL,
                     c3                INTEGER  NOT NULL,
                     c4                INTEGER  NOT NULL,
                     c5                INTEGER  NOT NULL,
                     duration          REAL     NOT NULL,
                     passed            INTEGER  NOT NULL,
                     result            TEXT     NOT NULL)
                  """)

      cur.execute("""
                  CREATE TABLE testlog (
                     testresult_id     TEXT     NOT NULL,
                     lineno            INTEGER  NOT NULL,
                     timestamp         REAL     NOT NULL,
                     sessionidx        INTEGER,
                     sessionid         TEXT,
                     line              TEXT     NOT NULL,
                     PRIMARY KEY (testresult_id, lineno))
                  """)

      ## add: testee, testcase, testspec?

   ## Cases are identified by "caseSetName", a string, e.g. "wamp"
   ## and a "caseIndex", e.g. [2, 2, 5, 11].
   ##
   ## Testees are identified by
   ##
   ## hostname, IP, port
   ## WAMP ident
   ## specname

   def _checkDb(self):
      pass


   def getTestCaseCategories(self, caseSet = "wamp"):
      if caseSet == "wamp":
         pass
      else:
         raise Exception("no such case set")


   def _checkTestSpec(self, spec):
      if type(spec) != dict:
         raise Exception("test spec must be a dict")

      sig_spec = {'name': (True, [str, unicode]),
                  'desc': (False, [str, unicode]),
                  'mode': (True, [str, unicode]),
                  'caseset': (True, [str, unicode]),
                  'cases': (True, [list]),
                  'exclude': (False, [list]),
                  'options': (False, [dict]),
                  'testees': (True, [list])}

      sig_spec_modes = ['fuzzingwampclient']
      sig_spec_casesets = ['wamp']

      sig_spec_options = {'rtt': (False, [int, float]),
                          'randomize': (False, [bool]),
                          'parallel': (False, [bool])}

      sig_spec_testee = {'name': (True, [str, unicode]),
                         'desc': (False, [str, unicode]),
                         'url': (True, [str, unicode]),
                         'auth': (False, [dict]),
                         'exclude': (False, [list]),
                         'options': (False, [dict])}

      sig_spec_testee_auth = {'authKey': (True, [str, unicode, types.NoneType]),
                              'authSecret': (False, [str, unicode, types.NoneType]),
                              'authExtra': (False, [dict])}

      sig_spec_testee_options = {'rtt': (False, [int, float])}


      def verifyDict(obj, sig, signame):
         for att in obj:
            if att not in sig.keys():
               raise Exception("invalid attribute '%s' in %s" % (att, signame))

         for key, (required, atypes) in sig.items():
            if required and not obj.has_key(key):
               raise Exception("missing mandatory %s attribute '%s'" % (signame, key))
            if obj.has_key(key) and type(obj[key]) not in atypes:
               raise Exception("invalid type '%s' for %s attribute '%s'" % (type(sig[key]), signame, key))

      verifyDict(spec, sig_spec, 'test specification')
      if spec.has_key('options'):
         verifyDict(spec['options'], sig_spec_options, 'test options')

      for testee in spec['testees']:
         verifyDict(testee, sig_spec_testee, 'testee description')

         if testee.has_key('auth'):
            verifyDict(testee['auth'], sig_spec_testee_auth, 'testee authentication credentials')

         if testee.has_key('options'):
            verifyDict(testee['options'], sig_spec_testee_options, 'testee options')

      if spec['mode'] not in sig_spec_modes:
         raise Exception("invalid mode '%s' in test specification" % spec['mode'])

      if spec['caseset'] not in sig_spec_casesets:
         raise Exception("invalid caseset '%s' in test specification" % spec['caseset'])


   def _loadTestSpec(self, specData):
      try:
         spec = json.loads(specData)
      except Exception, e:
         raise Exception("Error: invalid JSON data - %s" % e)
      self._checkTestSpec(spec)
      return spec


   def importSpec(self, specData):
      spec = self._loadTestSpec(specData)

      name = spec['name']
      mode = spec['mode']
      caseset = spec['caseset']
      desc = spec.get('desc', None)

      def do(txn):
         data = json.dumps(spec, ensure_ascii = False, allow_nan = False, separators = (',', ':'), indent = None)

         now = utcnow()
         id = newid()

         txn.execute("SELECT id, spec FROM testspec WHERE name = ? AND valid_to IS NULL", [name])
         res = txn.fetchone()
         op = None

         if res is not None:
            currId, currSpec = res
            if currSpec == data:
               return (op, currId, name)
            else:
               beforeId = currId
               op = 'U'
               txn.execute("UPDATE testspec SET valid_to = ? WHERE id = ?", [now, currId])
         else:
            beforeId = None
            op = 'I'
            
         txn.execute("INSERT INTO testspec (id, before_id, valid_from, name, desc, mode, caseset, spec) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [id, beforeId, now, name, desc, mode, caseset, data])
         return (op, id, name)

      return self._dbpool.runInteraction(do)


   def getSpec(self, specId):

      def do(txn):

         txn.execute("SELECT spec FROM testspec WHERE id = ?", [specId])
         res = txn.fetchone()

         if res is None:
            raise Exception("no test specification with ID '%s'" % specId)
         else:
            return json.loads(res[0])

      return self._dbpool.runInteraction(do)


   def getSpecByName(self, specName):

      def do(txn):

         txn.execute("SELECT id, spec FROM testspec WHERE name = ? AND valid_to IS NULL", [specName])
         res = txn.fetchone()

         if res is None:
            raise Exception("no (active) test specification with name '%s'" % specName)
         else:
            id, data = res
            return (id, json.loads(data))

      return self._dbpool.runInteraction(do)


   def newRun(self, specId):

      def do(txn):
         txn.execute("SELECT mode FROM testspec WHERE id = ? AND valid_to IS NULL", [specId])
         res = txn.fetchone()
         if res is None:
            raise Exception("no such spec or spec not active")

         mode = res[0]
         if not mode in ITestDb.TESTMODES:
            raise Exception("mode '%s' invalid or not implemented" % mode)

         id = newid()
         now = utcnow()
         env = envinfo()
         txn.execute("INSERT INTO testrun (id, testspec_id, env, started) VALUES (?, ?, ?, ?)", [id, specId, json.dumps(env), now])
         return id

      return self._dbpool.runInteraction(do)


   def _saveResult_dstyle(self, runId, result):
      """
      Deferred style version of saveResult(). Just for checking
      if inline deferreds trigger any issues together with ADBAPI.
      """
      dr = Deferred()
      d1 = self._dbpool.runQuery("SELECT started, ended FROM testrun WHERE id = ?", [runId])

      def found(res):
         started, ended = res[0]
         id = newid()
         d2 = self._dbpool.runQuery("INSERT INTO testcase (id, testrun_id, result) VALUES (?, ?, ?)", [id, runId, json.dumps(result)])

         def saved(res):
            dr.callback(id)
         d2.addCallback(saved)

      d1.addCallback(found)
      return dr


   def saveResult(self, runId, testRun, test, result):

      if False:
         print
         print result.passed
         print result.expected
         print result.observed
         print result.started
         print result.ended
         print result.log
         print
         print test.index
         print test.description
         print test.expectation
         print test.testee
         print

      def do(txn):
         ## verify that testrun exists and is not closed already
         ##
         txn.execute("SELECT started, ended FROM testrun WHERE id = ?", [runId])
         res = txn.fetchone()
         if res is None:
            raise Exception("no such test run")
         if res[1] is not None:
            raise Exception("test run already closed")

         ## save test case results with foreign key to test run
         ##
         id = newid()
         now = utcnow()

         ci = []
         for i in xrange(5):
            if len(test.index) > i:
               ci.append(test.index[i])
            else:
               ci.append(0)

         txn.execute("""
            INSERT INTO testresult
               (id, testrun_id, inserted, testee, c1, c2, c3, c4, c5, duration, passed, result)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
               id,
               runId,
               now,
               testRun.testee.name,
               ci[0],
               ci[1],
               ci[2],
               ci[3],
               ci[4],
               result.ended - result.started,
               1 if result.passed else 0,
               result.serialize()])

         ## save test case log with foreign key to test result
         ##
         lineno = 1
         for l in result.log:
            txn.execute("""
               INSERT INTO testlog
                  (testresult_id, lineno, timestamp, sessionidx, sessionid, line)
                     VALUES (?, ?, ?, ?, ?, ?)
               """, [
               id,
               lineno,
               l[0],
               l[1],
               l[2],
               l[3]])
            lineno += 1

         return id

      return self._dbpool.runInteraction(do)


   def closeRun(self, runId):

      def do(txn):
         now = utcnow()

         ## verify that testrun exists and is not closed already
         ##
         txn.execute("SELECT started, ended FROM testrun WHERE id = ?", [runId])
         res = txn.fetchone()
         if res is None:
            raise Exception("no such test run")
         if res[1] is not None:
            raise Exception("test run already closed")

         ## close test run
         ##
         txn.execute("UPDATE testrun SET ended = ? WHERE id = ?", [now, runId])

      return self._dbpool.runInteraction(do)


   def getTestResult(self, resultId):

      def do(txn):
         txn.execute("SELECT id, testrun_id, testee, c1, c2, c3, c4, c5, passed, duration, result FROM testresult WHERE id = ?", [resultId])
         res = txn.fetchone()
         if res is None:
            raise Exception("no such test result")
         id, runId, testeeName, c1, c2, c3, c4, c5, passed, duration, data = res

         caseName = "WampCase" + '.'.join([str(x) for x in [c1, c2, c3, c4, c5]])

         result = TestResult()
         result.deserialize(data)
         result.id, result.runId, result.testeeName, result.caseName = id, runId, testeeName, caseName

         result.log = []
         txn.execute("SELECT timestamp, sessionidx, sessionid, line FROM testlog WHERE testresult_id = ? ORDER BY lineno ASC", [result.id])
         for l in txn.fetchall():
            result.log.append(l)

         return result

      return self._dbpool.runInteraction(do)


   def getTestRunIndex(self, runId):

      def do(txn):
         txn.execute("SELECT id, testee, c1, c2, c3, c4, c5, passed, duration FROM testresult WHERE testrun_id = ?", [runId])
         res = txn.fetchall()
         return [{'id': row[0],
                  'testee': row[1],
                  'c1': row[2],
                  'c2': row[3],
                  'c3': row[4],
                  'c4': row[5],
                  'c5': row[6],
                  'passed': row[7] != 0,
                  'duration': row[8]} for row in res]

      return self._dbpool.runInteraction(do)


   def getTestRunSummary(self, runId):

      def do(txn):

         ## verify that testrun exists and is not closed already
         ##
         txn.execute("SELECT started, ended FROM testrun WHERE id = ?", [runId])
         res = txn.fetchone()
         if res is None:
            raise Exception("no such test run")
         if res[1] is None:
            print "Warning: test run not closed yet"

         txn.execute("SELECT testee, SUM(passed), COUNT(*) FROM testresult WHERE testrun_id = ? GROUP BY testee", [runId])
         res = txn.fetchall()
         r = {}
         for row in res:
            testee, passed, count = row
            r[testee] = {'name': testee,
                         'passed': passed,
                         'failed': count - passed,
                         'count': count}
         return [r[k] for k in sorted(r.keys())]

      return self._dbpool.runInteraction(do)


   #@exportRpc => FIXME: add WAMP API
   def getTestRuns(self, limit = 10):

      def do(txn):

         txn.execute("""
            SELECT r.id, s.mode, r.started, r.ended
               FROM testrun r INNER JOIN testspec s ON r.testspec_id = s.id
                  ORDER BY r.started DESC LIMIT ?""", [limit])
         res = txn.fetchall()
         return res

      return self._dbpool.runInteraction(do)

