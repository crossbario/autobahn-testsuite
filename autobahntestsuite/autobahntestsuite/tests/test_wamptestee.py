from twisted.trial import unittest
from autobahntestsuite import wamptestee
import types
import datetime


class TestEchoService(unittest.TestCase):

    
    def setUp(self):
        self.echo_service = wamptestee.EchoService()

        
    def testEcho(self):
        for val in ["Hallo", 5, -1000, datetime.datetime.now(), True]:
            self.assertEquals(self.echo_service.echo(val), val)


            
class TestStringService(unittest.TestCase):

    
    def setUp(self):
        self.string_service = wamptestee.StringService()

        
    def testConcat(self):
        self.assertEquals(self.string_service.concat("a", "b"), "ab")


class TestNumberService(unittest.TestCase):

    def setUp(self):
        self.number_service = wamptestee.NumberService()


    def testAddNumbers(self):
        self.assertEquals(self.number_service.add(1, 2, 3), 6)
        self.assertEquals(self.number_service.add(5, 0), 5)
        self.assertRaises(AssertionError, self.number_service.add, 5)
        self.assertRaises(AssertionError, self.number_service.add,
                          1, "5")

class TestTesteeWampServer(unittest.TestCase):


    def setUp(self):
        self.testee = wamptestee.TesteeWampServerProtocol()
        self.testee.debugWamp = True # mock setup of debugWamp
        self.testee.procs = {} # mock setup of `procs` attribute
        self.testee.initializeServices()


    def testAttributeSetup(self):
        self.failUnless(hasattr(self.testee, "echo_service"),
                        "Attribute `echo_service` is missing.")
        self.assertEquals(self.testee.echo_service.__class__,
                          wamptestee.EchoService)
        self.failUnless(hasattr(self.testee, "string_service"),
                        "Attribute `string_service` is missing.")
        self.assertEquals(self.testee.string_service.__class__,
                          wamptestee.StringService)


    def testRegistrations(self):
        for case_number in [wamptestee.ECHO_NUMBER_ID,
                            wamptestee.ECHO_STRING_ID]:
            for idx in range(1, 5):
                self._checkUriSetup(wamptestee.EchoService, case_number, idx)
        self._checkUriSetup(wamptestee.EchoService,
                            wamptestee.ECHO_DATE_ID)
        self._checkUriSetup(wamptestee.StringService,
                            wamptestee.CONCAT_STRINGS_ID)
        self._checkUriSetup(wamptestee.NumberService,
                            wamptestee.ADD_TWO_NUMBERS_ID)
        self._checkUriSetup(wamptestee.NumberService,
                            wamptestee.ADD_THREE_NUMBERS_ID)


    def _checkUriSetup(self, service_cls, case_number, ref=None):
        uri = wamptestee.setupUri(case_number, ref)
        self.failUnless(uri in self.testee.procs)
        service, method, flag = self.testee.procs[uri]
        self.failUnless(isinstance(service, service_cls))
        self.assertEquals(type(method), types.MethodType)
        self.assertEquals(flag, False)
