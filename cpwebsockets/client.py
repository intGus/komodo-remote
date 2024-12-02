import binascii
import random
import ssl
import socketpool as socket
import adafruit_logging as logging

from .protocol import Websocket, urlparse

LOGGER = logging.getLogger(__name__)

def read_line(sock, buffer_size=1024):
    """
    Read a line from the socket using recv_into. Stops at '\r\n'.
    """
    buffer = bytearray(buffer_size)  # Pre-allocate buffer
    line = b""
    
    while True:
        bytes_read = sock.recv_into(buffer, 1)  # Read one byte at a time
        if bytes_read == 0:
            break  # End of stream
        line += buffer[:bytes_read]
        if line.endswith(b'\r\n'):  # Check for end of line
            break
    return line

class WebsocketClient(Websocket):
    is_client = True

def connect(uri, radio):
    """
    Connect a websocket.
    """

    uri = urlparse(uri)
    assert uri

    if __debug__: LOGGER.debug("open connection %s:%s",
                                uri.hostname, uri.port)

    sock = socket.SocketPool(radio).socket()
    addr = socket.SocketPool(radio).getaddrinfo(uri.hostname, uri.port)
    sock.connect(addr[0][4])
    
    if uri.protocol == 'wss':
        ssl_context = ssl.create_default_context()
        sock = ssl_context.wrap_socket(sock, server_hostname=uri.hostname)

    def send_header(header, *args):
        if __debug__: LOGGER.debug(str(header), *args)
        sock.send(header % args + '\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                    for _ in range(16)))[:-1]

    send_header(b'GET %s HTTP/1.1', uri.path or '/')
    send_header(b'Host: %s:%s', uri.hostname, uri.port)
    send_header(b'Connection: Upgrade')
    send_header(b'Upgrade: websocket')
    send_header(b'Sec-WebSocket-Key: %s', key)
    send_header(b'Sec-WebSocket-Version: 13')
    send_header(b'Origin: http://{hostname}:{port}'.format(
        hostname=uri.hostname,
        port=uri.port)
    )
    send_header(b'')

    header = read_line(sock)[:-2]
    assert header.startswith(b'HTTP/1.1 101 '), header

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        if __debug__: LOGGER.debug(str(header))
        header = read_line(sock)[:-2]

    return WebsocketClient(sock)