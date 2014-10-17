from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


class ClosingServerProtocol(Protocol):

   def connectionMade(self):
      self.transport.loseConnection()


class ClosingServerFactory(Factory):

   protocol = ClosingServerProtocol



endpoint = TCP4ServerEndpoint(reactor, 9001)
endpoint.listen(ClosingServerFactory())
reactor.run()
