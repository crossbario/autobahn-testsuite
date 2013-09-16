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

   session.call("testdb:getTestRuns", 30).then(
      function (res) {
         for (var r in res) {
            console.log(res[r]);
         }
      }, ab.log);
}

function startTestRun() {
   session.call("testrunner:run", "Local WAMP Dual").then(
      function (res) {
         var runId = res[0];
         var resultIds = res[1];
         console.log(runId, resultIds.length);
      }, ab.log);
}