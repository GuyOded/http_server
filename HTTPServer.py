"""
A simple http server.
Usage:
Construction- you must provide to the __init__ method an address(ip, port) and
              the absolute path of your server's root folder:
              HTTPServer(root=root_path, address=("127.0.0.1", 8080)
Starting the server- just use the method start_server from the main code.
                     Keep in mind that the method is a blocking code piece.
Termination- Just use a keyboard interrupt
"""

import socket
import constants
import HTTPRequest
import HTTPValidation
import HTTPResponse
import HTTPHeaders
import os.path as path

# determines how much information will be printed
# TODO: add a logfile
DEBUG_LEVEL = 0
# The methods the server supports at the moment
SUPPORTED_METHODS = ["GET"]
# Not Found HTML file name, must be in root
NOT_FOUND = "not_found.html"


class HTTPServer(object):
    def __init__(self, root, address=constants.ADDR):
        """
        Constructs an HTTPServer object
        :param root: The absolute path path of
        :param address: The server's socket will be bound to
                        the given address tuple e.g ("localhost", 8080)
        """
        self._root = root
        self._client = socket.socket()
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Some times the socket won't bind correctly and accept will raise
            # exception, therefore we set SO_REUSEADDR before binding
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self._socket.bind(address)
            if DEBUG_LEVEL >= 0:
                print "Listening on: {}".format(address)
            self._socket.listen(5)
        except socket.error as err:
            if DEBUG_LEVEL > 0:
                print "Got error: {}".format(err.message)

    def start_server(self):
        """
        Accepts a connection from a client and calls the
        method that handles request
        :return: None
        """
        while True:
            if DEBUG_LEVEL >= 0:
                print "Awaiting connection..."

            (client_socket, client_address) = self._socket.accept()
            if DEBUG_LEVEL >= 0:
                print "Got connection from: {}".format(client_address)

            self._client = client_socket

            self._listen_to_requests()

        self._socket.close()

    def _listen_to_requests(self):
        """
        Accepts a request from the client, closes the connection
        if the client terminated the connection, validates that the
        request is an http request, and sends it to _send_response
        for interpretation.
        :return: None
        """
        while True:
            try:
                request = self._client.recv(1024)
            except socket.error as err:
                if DEBUG_LEVEL >= 1:
                    print "Got socket error: {}".format(err.message)
                self._client.close()
                return True

            if not request:
                if DEBUG_LEVEL >= 0:
                    print "Closing connection"
                self._client.close()
                return True

            if DEBUG_LEVEL >= 2:
                print request

            if not HTTPValidation.validate_request(request):
                if DEBUG_LEVEL >= 0:
                    print "Invalid request, closing..."
                self._client.send(get_error_response())
                self._client.close()
                return True

            if not self._send_response(request):
                if DEBUG_LEVEL >= 0:
                    print "Closing connection..."
                self._client.close()
                return

    def _send_response(self, request):
        """
        given a valid request, sends an appropriate response to the client

        :param request: The request the server received from the client
        :return: False if the server is to close the connection with the
                 client, or True if the server should wait for the client's next
                 request.
        Won't raise any exception
        """
        request_line, headers = split_http_request(request)
        if DEBUG_LEVEL > 1:
            print "Request: {}\nHeaders: {}".format(request_line, headers)

        request = HTTPRequest.HTTPRequest(request_line, headers, DEBUG_LEVEL)

        if request.get_method() not in SUPPORTED_METHODS:
            if DEBUG_LEVEL >= 0:
                print "Unsupported request method"
            # send code 500
            self._client.send(get_error_response())
            return False

        # perform a small cast to index.html if the uri is empty
        url = request.get_url()[1:] if request.get_url()[0] == "/" else \
            request.get_url()

        # if url is / change to index.html
        url = "index.html" if url == "" else url

        full_file_path = path.join(self._root, url)
        if not path.isfile(full_file_path):
            if DEBUG_LEVEL >= 0:
                print "File: {} not found".format(full_file_path)
            # send 404 Not Found response
            self._client.send(self._get_404_response())
            return True

        requested_file = open(full_file_path, "r")
        data = requested_file.read()
        requested_file.close()

        headers = HTTPHeaders.HTTPHeaders()
        add_default_headers(headers)
        headers["Content-Length"] = str(len(data))

        response = HTTPResponse.HTTPResponse(version=1.0, status_code=200,
                                             phrase="OK", headers=headers)
        self._client.send(response.build_response() + data)
        return True

    def _get_404_response(self):
        """
        builds a typical 404 http response
        :return: an http not found response
        """
        response = HTTPResponse.HTTPResponse(version=1.0, status_code=404,
                                             phrase="Not Found")
        try:
            file_path = path.join(self._root, NOT_FOUND)
            f = open(file_path)
        except IOError:
            message = "<body><h1>Not Found</h1></body>"
            if DEBUG_LEVEL >= 2:
                print "File {} wasn't found in root"
        else:
            message = f.read()
            f.close()

        headers = HTTPHeaders.HTTPHeaders()
        add_default_headers(headers)
        headers["Content-Length"] = str(len(message))
        headers["Content-Type"] = "text/html"
        response.set_headers(headers)

        response.set_data(message)

        return response.build_response()


def get_error_response():
    """
    builds a typical http error response
    :return: an http error response
    """
    response = HTTPResponse.HTTPResponse(version=1.0, status_code=500,
                                         phrase="Internal Error")
    headers = HTTPHeaders.HTTPHeaders()
    add_default_headers(headers)
    headers["Content-Length"] = str(0)
    headers["Connection"] = "close"
    response.set_headers(headers)

    return response.build_response()


def add_default_headers(headers):
    """
    The following headers are usually added to an http message
    so this function adds them to a headers object instead of adding
    them manually in the code
    :param headers: The headers will be added to this argument
    :return: None
    """
    headers["Allow"] = ", ".join(SUPPORTED_METHODS)
    headers["Connection"] = "keep-alive"
    headers["Date"] = get_rfc_822_time()


def get_rfc_822_time():
    """
    :return: an rfc 822 compliant datetime string
    """
    from datetime import datetime
    from time import gmtime, strftime
    dt = datetime.now()
    today = dt.strftime("%A")[:3]
    month = dt.strftime("%B")[:3]
    time = dt.strftime("%H:%M:%S")
    tz = strftime("%Z", gmtime())
    return "{}, {} {} {} {} {}".format(today, dt.strftime("%d"), month,
                                       dt.strftime("%Y"), time, tz)


def split_http_request(request):
    """
    Splits the raw request gotten from client to two separate
    strings- request line and headers
    :param request:the request/response string
    :return:a tuple consisting of the request line and the headers
            separated
    """
    headers_start = request.find(constants.CRLF)
    if headers_start == -1:
        if DEBUG_LEVEL > 1:
            print request
        raise ValueError("No CR LF found in request")

    request_status_line = request[:headers_start]
    headers = request[headers_start + len(constants.CRLF):]
    if not headers:
        return request_status_line, ""

    if headers.find(constants.CRLF * 2) == -1:
        if DEBUG_LEVEL >= 1:
            print headers
        raise ValueError("End of headers not found")

    return request_status_line, headers
