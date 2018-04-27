from builtins import range
from twisted.trial import unittest
from autobahntestsuite import wamptestee
import types
import datetime


class TestEchoService(unittest.TestCase):
    """
    This test case checks if the echo service behaves as expected.
    """
    
    def setUp(self):
        self.echo_service = wamptestee.EchoService()

        
    def testEcho(self):
        """
        The echo service should echo received parameters correctly,
        regardless of their type.
        """
        for val in ["Hallo", 5, -1000, datetime.datetime.now(), True]:
            self.assertEquals(self.echo_service.echo(val), val)


            
class TestStringService(unittest.TestCase):
    """
    This test case checks if the string service behaves as expected.
    """

    
    def setUp(self):
        self.string_service = wamptestee.StringService()

        
    def testConcat(self):
        """
        The string service should concatenate strings correctly.
        """
        self.assertEquals(self.string_service.concat("a", "b"), "ab")
        self.assertEquals(self.string_service.concat("", "xxx"), "xxx")
        self.assertEquals(self.string_service.concat("", ""), "")


class TestNumberService(unittest.TestCase):
    """
    This test case checks if the number service behaves as expected.
    """

    def setUp(self):
        self.number_service = wamptestee.NumberService()


    def testAddIntegers(self):
        """
        The number service should add integers correctly.
        """
        self.assertEquals(self.number_service.add(1, 2, 3), 6)
        self.assertEquals(self.number_service.add(5, 0), 5)

    def testAddFloats(self):
        """
        The number service should add floats correctly.
        """
        # Use assertAlmostEquals to handle the (inevitable) rounding error.
        self.assertAlmostEquals(self.number_service.add(1.3, 2.9, 3.6), 7.8)
        self.assertEquals(self.number_service.add(5.3, 0.0), 5.3)

    def testAddingSingleNumber(self):
        """
        The number service should raise an assertion error if one
        tries to add just one number.
        """
        self.assertRaises(AssertionError, self.number_service.add, 5)

    def testAddStringToNumber(self):
        """
        The number service should raise an assertion error if one
        tries to add a string to a number.
        """
        self.assertRaises(AssertionError, self.number_service.add,
                          1, "5")


class TestTesteeWampServer(unittest.TestCase):
    """
    This test case checks if the testee WAMP server protocol behaves
    as expected.
    """

    
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
