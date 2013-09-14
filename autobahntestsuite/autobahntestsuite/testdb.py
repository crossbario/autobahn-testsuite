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

import os
import sqlite3

from twisted.python import log
from twisted.enterprise import adbapi

from autobahn.util import utcnow, newid
from autobahn.wamp import json_dumps
from twisted.internet.defer import Deferred

from zope.interface import implementer
from interfaces import ITestDb
from testrun import TestResult


@implementer(ITestDb)
class TestDb:
   """
   sqlite3 based test database implementing ITestDb. Usually, a single
   instance exists application wide (singleton). Test runners store their
   test results in the database and report generators fetch test results
   from the database. This allows to decouple application parts.
   """

   def __init__(self, dbfile = None):

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


   def _createDb(self):
      log.msg("creating test database at %s .." % self._dbfile)
      db = sqlite3.connect(self._dbfile)
      cur = db.cursor()
      cur.execute("""
                  CREATE TABLE testrun (
                     id                TEXT     PRIMARY KEY,
                     mode              TEXT     NOT NULL,
                     started           TEXT     NOT NULL,
                     ended             TEXT,
                     spec              TEXT     NOT NULL)
                  """)

      cur.execute("""
                  CREATE TABLE testresult (
                     id                TEXT     PRIMARY KEY,
                     testrun_id        TEXT     NOT NULL,
                     testee_name       TEXT     NOT NULL,
                     passed            INTEGER  NOT NULL,
                     duration          REAL     NOT NULL,
                     result            TEXT     NOT NULL)
                  """)

      cur.execute("""
                  CREATE TABLE testlog (
                     testresult_id     TEXT     NOT NULL,
                     seq               INTEGER  NOT NULL,
                     timestamp         REAL     NOT NULL,
                     session_index     INTEGER,
                     session_id        TEXT,
                     msg               TEXT     NOT NULL,
                     PRIMARY KEY (testresult_id, seq))
                  """)

      ## add: testee, testcase, testspec?


   def _checkDb(self):
      pass


   def newRun(self, mode, spec):
      if not mode in ITestDb.TESTMODES:
         raise Exception("mode '%s' invalid or not implemented" % mode)
      now = utcnow()
      id = newid()

      def do(txn):
         txn.execute("INSERT INTO testrun (id, mode, started, spec) VALUES (?, ?, ?, ?)", [id, mode, now, json_dumps(spec)])
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
         d2 = self._dbpool.runQuery("INSERT INTO testcase (id, testrun_id, result) VALUES (?, ?, ?)", [id, runId, json_dumps(result)])

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
         print test.name
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
         txn.execute("INSERT INTO testresult (id, testrun_id, testee_name, passed, duration, result) VALUES (?, ?, ?, ?, ?, ?)", [id, runId, testRun.testee.name, result.passed, result.ended - result.started, result.serialize()])

         ## save test case log with foreign key to test result
         ##
         seq = 1
         for l in result.log:
            txn.execute("INSERT INTO testlog (testresult_id, seq, timestamp, session_index, session_id, msg) VALUES (?, ?, ?, ?, ?, ?)", [id, seq, l[0], l[1], l[2], l[3]])
            seq += 1

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
         txn.execute("SELECT id, testrun_id, result FROM testresult WHERE id = ?", [resultId])
         res = txn.fetchone()
         if res is None:
            raise Exception("no such test result")
         id, runId, data = res

         result = TestResult()
         result.deserialize(data)
         result.id, result.runId = id, runId

         result.log = []
         txn.execute("SELECT timestamp, session_index, session_id, msg FROM testlog WHERE testresult_id = ? ORDER BY seq ASC", [result.id])
         for l in txn.fetchall():
            result.log.append(l)

         return result

      return self._dbpool.runInteraction(do)


   def getTestRunIndex(self, runId):

      def do(txn):
         txn.execute("SELECT id, testee_name, passed, duration FROM testresult WHERE testrun_id = ?", [runId])
         res = txn.fetchall()
         return [{'id': row[0],
                  'testee': row[1],
                  'passed': row[2] != 0,
                  'duration': row[3]} for row in res]

      return self._dbpool.runInteraction(do)


   def getTestRunSummary(self, runId):

      def do(txn):

         ## verify that testrun exists and is not closed already
         ##
         txn.execute("SELECT mode, started, ended, spec FROM testrun WHERE id = ?", [runId])
         res = txn.fetchone()
         if res is None:
            raise Exception("no such test run")
         if res[1] is None:
            print "Warning: test run not closed yet"

         txn.execute("SELECT testee_name, passed, COUNT(*) FROM testresult WHERE testrun_id = ? GROUP BY testee_name, passed", [runId])
         res = txn.fetchall()
         r = {}
         for row in res:
            testee_name, passed, cnt = row
            if not r.has_key(testee_name):
               r[testee_name] = {'name': testee_name, 'passed': 0, 'failed': 0}
            if passed:
               r[testee_name]['passed'] = cnt
            else:
               r[testee_name]['failed'] = cnt
         return [r[k] for k in sorted(r.keys())]

      return self._dbpool.runInteraction(do)


   #@exportRpc => FIXME: add WAMP API
   def getTestRuns(self, limit = 10):

      def do(txn):

         txn.execute("SELECT id, mode, started, ended FROM testrun ORDER BY started DESC LIMIT ?", [limit])
         res = txn.fetchall()
         return res

      return self._dbpool.runInteraction(do)
