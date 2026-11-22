"""Echo server for the fuzzingclient, using the image's own autobahn library.

permessage-deflate is accepted so the 12.x/13.x compression cases run too.
"""
import sys

from autobahn.twisted.websocket import (
    WebSocketServerFactory,
    WebSocketServerProtocol,
    listenWS,
)
from autobahn.websocket.compress import (
    PerMessageDeflateOffer,
    PerMessageDeflateOfferAccept,
)
from twisted.internet import reactor


class EchoServerProtocol(WebSocketServerProtocol):
    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)


def accept(offers):
    for offer in offers:
        if isinstance(offer, PerMessageDeflateOffer):
            return PerMessageDeflateOfferAccept(offer)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "ws://127.0.0.1:9001"
    factory = WebSocketServerFactory(url)
    factory.protocol = EchoServerProtocol
    factory.setProtocolOptions(perMessageCompressionAccept=accept)
    listenWS(factory)
    reactor.run()
