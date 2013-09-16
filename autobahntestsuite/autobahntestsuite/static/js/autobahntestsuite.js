/* global document: false, console: false, ab: true, $: true, JustGage: false, getRandomInt: false */

"use strict";

var session = null;

start();


function start() {

   // turn on WAMP debug output
   // ab.debug(true, false, false);

   // use jQuery deferreds
   ab.Deferred = $.Deferred;

   // Connect to Tavendo WebMQ ..
   //
   ab.connect("ws://127.0.0.1:8090/ws",
      function (sess) {
         console.log("connected");
         session = sess;
         main();
      },
      function (code, reason, detail) {
         console.log("connection lost", reason);
         session = null;
      }
   );
}


function main() {
   session.prefix("testdb", "http://api.testsuite.autobahn.ws/testdb/");
   session.prefix("testrunner", "http://api.testsuite.autobahn.ws/testrunner/");

}


function test_getTestRuns (limit) {
   if (limit === undefined) limit = 5;

   session.call("testdb:getTestRuns", limit).then(
      function (res) {
         for (var r in res) {
            console.log(res[r]);
         }
      },
      ab.log
   );
}


function test_startRun (specName) {
   if (specName === undefined) specName = "Local WAMP Dual";

   session.call("testrunner:run", specName).then(
      function (res) {
         var runId = res[0];
         var resultIds = res[1];
         console.log("New test run started", runId, resultIds.length);
      },
      ab.log
   );
}


function test_importSpec() {

   var spec = {
      "name": "Local WAMP 1",
      "desc": "Quick test case set targeting a locally running AutobahnPython based WAMP server.",

      "mode": "fuzzingwampclient",  

      "caseset": "wamp",
      "cases": ["*"],
      "exclude": [],

      "options": {
         "rtt": 0.05,
         "randomize": false,
         "parallel": false
      },

      "testees": [
         {
            "name": "AutobahnPython",
            "desc": "This runs 'testeewampserver' from wstest.",
            "url": "ws://127.0.0.1:9001",
            "exclude": [],
            "options":  {
               "rtt": 0.01
            }
         }
      ]
   };

   session.call("testdb:importSpec", spec).then(
      function (res) {
         var op = res[0];
         var id = res[1];
         switch (op) {
            case "U":
               console.log("Updated existing spec", id);
               break;
            case "I":
               console.log("Imported new spec", id);
               break;
            default:
               console.log("Spec unchanged", id);
         }
      },
      ab.log
   );
}


function test_getSpecByName(specName) {

   if (!specName) specName = "Local WAMP Dual";

   session.call("testdb:getSpecByName", specName).then(
      function (res) {
         var specId = res[0];
         var spec = res[1];
         console.log("Spec", specId, spec);
      },
      ab.log
   );
}


function test_getSpec(i, specId) {
   session.call("testdb:getSpec", specId).then(
      function (res) {
         console.log("Spec", i, specId, res);
      },
      ab.log
   );
}


function test_getSpecs() {

   var activeOnly = true; // default => only retrieve active specs

   session.call("testdb:getSpecs", activeOnly).then(
      function (res) {
         for (var i = 0; i < res.length; ++i) {
            var spec = res[i];
            console.log("Spec Meta", i, spec);
            test_getSpec(i, spec.id);
         }
      },
      ab.log
   );
}