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

from autobahn.wamp1 import protocol as wamp
import types


# Test case IDs for the echo service
ECHO_NUMBER_ID = "3.1.1"
ECHO_STRING_ID = "3.1.2"
ECHO_DATE_ID = "1.3.1"


class EchoService(object):
    """
    Provides a simple 'echo' service: returns whatever it receives.
    """

    def echo(self, val):
        return val


# Test case ID for the string service
CONCAT_STRINGS_ID = "1.1.5"


class StringService(object):
    """
    Provides basic string services.
    """

    def concat(self, str_1, str_2):
        """
        Concatenates two strings and returns the resulting string.
        """
        assert type(str_1) == types.StringType
        assert type(str_2) == types.StringType
        return str_1 + str_2


# Test case IDs for the number service
ADD_TWO_NUMBERS_ID = "1.2.4"
ADD_THREE_NUMBERS_ID = "1.2.5"


class NumberService(object):
    """
    Provides a simple service for calculating with numbers.
    """

    def add(self, *numbers):
        """
        Adds an unspecified number of numbers and returns the result.
        """
        assert len(numbers) >= 2
        assert [n for n in numbers if type(n) not in [types.IntType,
                                                      types.FloatType,
                                                      types.LongType]] == []
        return sum(numbers)


# Template for creating an URI used for registering a method
URI_CASE_TEMPLATE = "http://api.testsuite.wamp.ws/case/%s"


def setupUri(case, ref=None):
    """
    Prepares the URI for registering a certain service.
    """
    assert type(ref) in (types.NoneType, types.IntType)
    uri = URI_CASE_TEMPLATE % case
    if ref is not None:
        uri = "%s#%s" % (uri, ref)
    return uri



class MyTopicService:

   def __init__(self, allowedTopicIds):
      self.allowedTopicIds = allowedTopicIds
      self.serial = 0


   @wamp.exportSub("foobar", True)
   def subscribe(self, topicUriPrefix, topicUriSuffix):
      """
      Custom topic subscription handler.
      """
      print "client wants to subscribe to %s%s" % (topicUriPrefix, topicUriSuffix)
      try:
         i = int(topicUriSuffix)
         if i in self.allowedTopicIds:
            print "Subscribing client to topic Foobar %d" % i
            return True
         else:
            print "Client not allowed to subscribe to topic Foobar %d" % i
            return False
      except:
         print "illegal topic - skipped subscription"
         return False


   @wamp.exportPub("foobar", True)
   def publish(self, topicUriPrefix, topicUriSuffix, event):
      """
      Custom topic publication handler.
      """
      print "client wants to publish to %s%s" % (topicUriPrefix, topicUriSuffix)
      try:
         i = int(topicUriSuffix)
         if type(event) == dict and event.has_key("count"):
            if event["count"] > 0:
               self.serial += 1
               event["serial"] = self.serial
               print "ok, published enriched event"
               return event
            else:
               print "event count attribute is negative"
               return None
         else:
            print "event is not dict or misses count attribute"
            return None
      except:
         print "illegal topic - skipped publication of event"
         return None



class TesteeWampServerProtocol(wamp.WampServerProtocol):
    """
    A WAMP test server for testing the AutobahnPython WAMP functionality.
    """


    def onSessionOpen(self):
        self.initializePubSub()
        self.initializeServices()
        self.debugWamp = True
        self.debugWs = False
        self.debug = False


    #@wamp.exportRpc("dispatch")
    def testDispatch(self, topic, event, options):
        """
        Simulate a server initiated event controlled by the tester.
        """
        if options.has_key('exclude'):
            exclude = options['exclude']
        else:
            excludeMe = options.get('excludeMe', None)
            if excludeMe is None or excludeMe == True:
                exclude = [self.session_id]
            else:
                exclude = []

        exclude = self.factory.sessionIdsToProtos(exclude)

        eligible = options.get('eligible', None)
        if eligible:
            eligible = self.factory.sessionIdsToProtos(eligible)

        self.factory.dispatch(topic, event, exclude = exclude, eligible = eligible)


    def initializeServices(self):
        """
        Initialize the services and register the RPC methods.
        """
        #self.registerForRpc("http://api.testsuite.wamp.ws/testee/control#", self)
        self.registerMethodForRpc("http://api.testsuite.wamp.ws/testee/control#dispatch", self, TesteeWampServerProtocol.testDispatch)

        self.echo_service = EchoService()
        self.string_service = StringService()
        self.number_service = NumberService()
        for case_id in [ECHO_NUMBER_ID, ECHO_STRING_ID]:
            for idx in range(1, 5):
                self.registerMethodForRpc(setupUri(case_id, idx),
                                          self.echo_service,
                                          EchoService.echo
                                          )
        self.registerMethodForRpc(setupUri(ECHO_DATE_ID),
                                  self.echo_service,
                                  EchoService.echo
                                  )
        self.registerMethodForRpc(setupUri(CONCAT_STRINGS_ID),
                                  self.string_service,
                                  StringService.concat
                                  )
        for case_id in [ADD_TWO_NUMBERS_ID, ADD_THREE_NUMBERS_ID]:
            self.registerMethodForRpc(setupUri(case_id),
                                  self.number_service,
                                  NumberService.add
                                  )

    def initializePubSub(self):
        ## Tests publish events to topics having this prefix.
        ##
        self.registerForPubSub("http://example.com/simple", True)

        ## Tests publish events to this topic expecting events
        ## to be dispatched. Tests also publish to topics with
        ## this URI as prefix, but then expect no dispatching to
        ## happen, since the URI was not registered
        ## with prefix = True.
        ##
        self.registerForPubSub("http://example.com/foobar")

        ## This topic is intentionally left unregistered
        ## Tests will publish to this topic and check that
        ## events are not dispatched.
        ##
        #self.registerForPubSub("http://example.com/barbaz")


        #self.registerForPubSub("http://example.com/event#", True)
        #self.registerForPubSub("http://example.com/event/simple")
        #self.topicservice = MyTopicService([1, 3, 7])
        #self.registerHandlerForPubSub(self.topicservice, "http://example.com/event/")


def startServer(wsuri, sslKey = None, sslCert = None, debug = False):
   factory = WampServerFactory(wsuri, self.debug)
   factory.protocol = TesteeWampServerProtocol

   if sslKey and sslCert:
      sslContext = ssl.DefaultOpenSSLContextFactory(sslKey, sslCert)
   else:
      sslContext = None

   listenWS(factory, sslContext)
   return True
