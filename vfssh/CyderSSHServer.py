import asyncio
import os
from asyncssh import SSHServer, ChannelOpenError, OPEN_ADMINISTRATIVELY_PROHIBITED, Error, create_server
import time
import json
from vfssh.CyderSSHSession import CyderSSHSession
from vfssh.CyderSSHTCPSession import CyderSSHTCPSession
import gconstant as gc
import traceback


class CyderSSHServer(SSHServer):
    #  Main SSH Server (Called every time a user attempt to connect to SSH)
    client = None

    def connection_requested(self, dest_host, dest_port, orig_host, orig_port):
        #  Base on the connection requested, Port 80 and 443 is allowed for Direct-TCP (SSH as Proxy)
        if dest_port == 80 or dest_port == 443:
            return CyderSSHTCPSession(self.client, dest_host, dest_port)
        else:
            raise ChannelOpenError(OPEN_ADMINISTRATIVELY_PROHIBITED, 'Only HTTP(80) or HTTPS(443) proxy allowed')

    def connection_made(self, conn):
        #  Self-explanatory
        self.client = conn.get_extra_info('socket')
        gc.LOG_DEBUG.debug(f'SSH Connection From: {self.client.getpeername()[0]}:{self.client.getpeername()[1]}')

    def connection_lost(self, exc):
        #  Self-explanatory
        if exc:
            # a = traceback.format_tb(exc.__traceback__, limit=-3)
            # for i in a:
            #     print(i.strip())
            gc.LOG_DEBUG.debug('SSH Connection Error: ' + str(exc))
        else:
            gc.LOG_DEBUG.debug('SSH Connection Closed')

    def begin_auth(self, username):
        return True

    def password_auth_supported(self):
        return True

    def kbdint_auth_supported(self):
        return False

    def validate_password(self, username, password):
        #  Logs each time a password is validated.
        data = {'timestamp': time.time(), 'protocol': 'SSH', 'username': username, 'password': password,
                'dst_ip': self.client.getsockname()[0], 'dst_port': self.client.getsockname()[1],
                'src_ip': self.client.getpeername()[0], 'src_port': self.client.getpeername()[1]}
        gc.LOG_CYDER.info(json.dumps(data))
        return True if [username, password] in gc.CREDENTIALS else False

    def session_requested(self):
        return CyderSSHSession(self.client)


async def start_server(host, port, banner, ssh_host_key='ssh_host_key'):
    await create_server(server_factory=CyderSSHServer, host=host, port=port,
                        server_host_keys=[ssh_host_key],
                        server_version=banner, login_timeout=120)


def start_ssh_server(host, port, banner):
    ssh_host_key = f'{os.path.dirname(os.path.realpath(__name__))}/configuration/key/{gc.HOST_MACHINE}/private.key'
    loop = asyncio.new_event_loop()

    try:
        loop.run_until_complete(start_server(host, port, banner, ssh_host_key))
    except (OSError, Error, KeyboardInterrupt) as e:
        print('Error {}'.format(e))
        exit(0)

    try:
        print('Started')
        loop.run_forever()
    except KeyboardInterrupt:
        exit(0)
