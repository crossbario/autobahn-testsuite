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
      function (session) {
         console.log("connected");
         main(session);
      },
      function (code, reason, detail) {
         console.log("connection lost", reason);
      }
   );
}

function main(session) {
   session.prefix("testdb", "http://api.testsuite.autobahn.ws/testdb/");
   session.call("testdb:getTestRuns", 30).then(
      function (res) {
         for (var r in res) {
            console.log(res[r]);
         }
      }, ab.log);
}