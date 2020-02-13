from flask import Flask, request, Response
from waitress import serve
import logging
import json
import time
import gconstant as gc


class LocalFlask(Flask):
    """
    A self-created Flask class to override the initialisation and process_response.
    This allows editing the HTTP banner response globally instead of a single page.

    :param banner: Defaults to 'None'. This is the HTTP Banner response.
        If this follows the default, a custom Cisco banner will be set.
    """

    def __init__(self, import_name, banner=None):
        if banner:
            self.banner = banner
        else:
            self.banner = 'Cisco IOS http config 7.0 (IOS 15.0)'
        super().__init__(import_name)

    def process_response(self, response):
        """
        Overrides the process_response function from Flask

        :param response: setting the response banner
        :return: response which is the banner
        """
        response.headers['server'] = self.banner
        super(LocalFlask, self).process_response(response)
        return response


app = LocalFlask(__name__)


@app.before_request
def require_auth():
    """
    Triggers the Basic Authentication through using the @app.before_request

    :return: 'True' if the username and password combination was correct,
        and 'Response of failed authentication' otherwise.
    """
    if request.authorization and request.authorization.username == 'you_cant_guess_this' \
            and request.authorization.password == 'you_really_cant_guess_this':
        return True
    else:

        try:
            username = request.authorization.username
            password = request.authorization.password
            data = {'timestamp': time.time(), 'protocol': 'HTTP', 'username': username,
                    'password': password, 'src_ip': request.remote_addr,
                    'dst_ip': request.host, 'src_port': request.environ.get('REMOTE_PORT')}
            gc.LOG_CYDER.info(json.dumps(data))
        except AttributeError:
            return Response(status=401, headers={'WWW-Authenticate': 'Basic realm="Login Required"'})

    # data = {'timestamp': time.time(), 'protocol': 'HTTP', 'username': username,
    #         'password': password, 'src_ip': str(address[0]),
    #         'dst_ip': client.getsockname()[0], 'source_port': address[1]}
    # logger.debug(json.dumps(data))
    return Response(status=401, headers={'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/')
def hello_world():
    return "<h1>I Can't Believe You Actually Found The Login Credentials!</h1>"


def start_http_server(host, port=80, banner=None):
    """
    Function to start the HTTP Server of Flask

    :param host: The IP address to bind the socket to.
        (0.0.0.0) for public and (127.0.0.1) for local
    :param port: The port to bind the socket to. Defaults to '80'
    :param banner: The response http banner
    """
    if banner:
        app.banner = banner
    serve(app, host=host, port=port, _quiet=True)


if __name__ == '__main__':
    start_http_server('0.0.0.0', 80, 'Cisco Fake')
