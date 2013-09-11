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
import sqlite3

from twisted.python import log
from twisted.enterprise import adbapi

from autobahn.util import utcnow, newid
from autobahn.wamp import json_loads, json_dumps
from twisted.internet.defer import Deferred



class TestDb:

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
                  CREATE TABLE kvstore (
                     key               TEXT     PRIMARY KEY,
                     value             TEXT     NOT NULL)
                  """)

      cur.execute("""
                  CREATE TABLE testrun (
                     id                TEXT     PRIMARY KEY,
                     mode              TEXT     NOT NULL,
                     started           TEXT     NOT NULL,
                     ended             TEXT,
                     spec              TEXT     NOT NULL)
                  """)

      cur.execute("""
                  CREATE TABLE testcase (
                     id                TEXT     PRIMARY KEY,
                     testrun_id        TEXT     NOT NULL,
                     result            TEXT     NOT NULL)
                  """)


   def _checkDb(self):
      pass


   def newRun(self, mode, spec):
      """
      Create a new testsuite run.

      :param mode: The testsuite mode.
      :type mode: str
      :param spec: The test specification.
      :type spec: object (a JSON serializable test spec)
      :returns str -- The testrun ID.
      """
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


   def saveResult(self, runId, result):

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
         txn.execute("INSERT INTO testcase (id, testrun_id, result) VALUES (?, ?, ?)", [id, runId, json_dumps(result)])
         return id

      return self._dbpool.runInteraction(do)


   def closeRun(self, runId):
      pass
