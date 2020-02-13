from twisted.conch.telnet import StatefulTelnetProtocol, OptionRefused, AlreadyNegotiating
from twisted.internet.error import ConnectionDone
from twisted.internet import reactor
from twisted.python.compat import iterbytes
from twisted.internet.protocol import ServerFactory
from twisted.conch.telnet import ITelnetProtocol, TelnetTransport, ECHO
from twisted.protocols.policies import TimeoutMixin
from twisted.conch.telnet import IAC, SB, NOP, DM, BRK, IP, AO, AYT, EC, EL, GA, WILL, WONT, DO, DONT, SE
import gconstant as gc
import json
import time
import signal

CUSTOM = ''
PORT_2323 = False


class TelnetEcho(StatefulTelnetProtocol):
    username = ''
    password = ''
    state = ''
    times_tried = 0

    def connectionMade(self):
        gc.LOG_DEBUG.debug(f"Telnet Connection From: {self.transport.getPeer().host} | {self.transport.getPeer().port}")
        global CUSTOM
        self.transport._write(CUSTOM.encode('raw_unicode_escape'))
        self.state = 'User'

    def _error_callback(self, failure):
        if failure.check(AlreadyNegotiating, OptionRefused, ConnectionDone):
            pass
        if failure.check(ConnectionDone):
            self.transport.loseConnection()
            return

    def lineReceived(self, line):
        self.transport.resetTimeout()
        if self.times_tried == 3:
            self.transport.loseConnection()
            return
        if self.state == 'User':
            self.username = line.strip()
            d = self.transport.will(ECHO)
            d.addErrback(self._error_callback)
            self.transport.write(b'Password: ')
            self.state = 'Password'
        elif self.state == 'Password':
            self.password = line.strip()
            if PORT_2323 is True:
                protocol = 'Telnet-2323'
            else:
                protocol = 'Telnet'
            data = {'timestamp': time.time(), 'protocol': protocol, 'username': self.username.decode('ISO-8859-1'),
                    'password': self.password.decode('ISO-8859-1'), 'src_ip': self.transport.getPeer().host,
                    'dst_ip': self.transport.getHost().host, 'src_port': self.transport.getPeer().port}
            gc.LOG_CYDER.info(json.dumps(data))
            self.times_tried += 1
            if self.times_tried == 3:
                self.transport.loseConnection()
                return
            d = self.transport.wont(ECHO)
            d.addErrback(self._error_callback)
            self.transport.write(b"\r\nAuthentication failed")
            self.transport.write(b"\r\nUsername: ")
            self.state = 'User'
        elif self.state == 'Prompt':
            if line.strip() == 'quit':
                self.transport.loseConnection()
                return
            self.sendLine(line)
            self.transport.write(b'> ')
        return


class CyderTelnetTransport(TelnetTransport, TimeoutMixin):

    def connectionMade(self):
        self.setTimeout(60)
        if self.protocolFactory is not None:
            self.protocol = self.protocolFactory(*self.protocolArgs, **self.protocolKwArgs)
            assert ITelnetProtocol.providedBy(self.protocol)
            try:
                factory = self.factory
            except AttributeError:
                pass
            else:
                self.protocol.factory = factory
            self.protocol.makeConnection(self)

    def dataReceived(self, data):
        ctrl_z = b'\xed'
        unknown = b'\x01'
        appDataBuffer = []

        for b in iterbytes(data):
            if self.state == 'data':
                if b == IAC:
                    self.state = 'escaped'
                elif b == b'\r':
                    self.state = 'newline'
                else:
                    appDataBuffer.append(b)
            elif self.state == 'escaped':
                if b == IAC:
                    appDataBuffer.append(b)
                    self.state = 'data'
                elif b == SB:
                    self.state = 'subnegotiation'
                    self.commands = []
                elif b in (NOP, DM, BRK, IP, AO, AYT, EC, EL, GA):
                    self.state = 'data'
                    if appDataBuffer:
                        self.applicationDataReceived(b''.join(appDataBuffer))
                        del appDataBuffer[:]
                    self.commandReceived(b, None)
                elif b in (WILL, WONT, DO, DONT):
                    self.state = 'command'
                    self.command = b
                elif b == ctrl_z or b == unknown:
                    appDataBuffer.append(b)
                    self.state = 'data'
                    # self.loseConnection()
                else:
                    raise ValueError("Stumped", b)
            elif self.state == 'command':
                self.state = 'data'
                commands = self.command
                del self.command
                if appDataBuffer:
                    self.applicationDataReceived(b''.join(appDataBuffer))
                    del appDataBuffer[:]
                self.commandReceived(commands, b)
            elif self.state == 'newline':
                self.state = 'data'
                if b == b'\n':
                    appDataBuffer.append(b'\n')
                elif b == b'\0':
                    appDataBuffer.append(b'\r')
                elif b == IAC:
                    # IAC isn't really allowed after \r, according to the
                    # RFC, but handling it this way is less surprising than
                    # delivering the IAC to the app as application data.
                    # The purpose of the restriction is to allow terminals
                    # to unambiguously interpret the behavior of the CR
                    # after reading only one more byte.  CR LF is supposed
                    # to mean one thing (cursor to next line, first column),
                    # CR NUL another (cursor to first column).  Absent the
                    # NUL, it still makes sense to interpret this as CR and
                    # then apply all the usual interpretation to the IAC.
                    appDataBuffer.append(b'\r')
                    self.state = 'escaped'
                else:
                    appDataBuffer.append(b'\r' + b)
            elif self.state == 'subnegotiation':
                if b == IAC:
                    self.state = 'subnegotiation-escaped'
                else:
                    self.commands.append(b)
            elif self.state == 'subnegotiation-escaped':
                if b == SE:
                    self.state = 'data'
                    commands = self.commands
                    del self.commands
                    if appDataBuffer:
                        self.applicationDataReceived(b''.join(appDataBuffer))
                        del appDataBuffer[:]
                    self.negotiate(commands)
                else:
                    self.state = 'subnegotiation'
                    self.commands.append(b)
            else:
                raise ValueError("How'd you do this?")

        if appDataBuffer:
            self.applicationDataReceived(b''.join(appDataBuffer))


def create_factory():
    factory = ServerFactory()
    factory.protocol = lambda: CyderTelnetTransport(TelnetEcho)
    return factory


def start_telnet_server(host, port, banner=None):
    """
    Starts the Fake Telnet Server

    :param host: The IP address to bind the socket to.
        (0.0.0.0) for public and (127.0.0.1) for local
        Defaults to 0.0.0.0
    :param port: The port to bind the socket to
    :param banner: The telnet banner
    """
    global CUSTOM
    global PORT_2323
    if banner:
        CUSTOM = banner
    if port == 2323:
        PORT_2323 = True
    my_factory = create_factory()
    reactor.listenTCP(port, my_factory, interface=host)
    reactor.run(installSignalHandlers=signal.SIGINT)
