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
import public_response_functions
from server_constants import *
import server_functions

# determines how much information will be printed
# TODO: add a logfile
DEBUG_LEVEL = 0


class HTTPServer(object):
    def __init__(self, root, restricted_folders,
                 restricted_page=RESTRICTED_HTML_PAGE, address=constants.ADDR):
        """
        Constructs an HTTPServer object
        :type root: str
        :param root: The absolute path path of
        :type restricted_folders: list
        :param restricted_folders: folders in root that are not to be accessed
        :type address: tuple
        :param address: The server's socket will be bound to
                        the given address tuple e.g ("localhost", 8080)
        """
        self._root = root
        self._restricted_folders = restricted_folders
        self._restricted_html = restricted_page
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
                self._client.send(public_response_functions.get_error_response())
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

        uri = request.get_uri_with_no_params()
        uri = uri[1:] if uri[0] == "/" else uri

        if uri in server_functions.AVAILABLE_FUNCTIONS.keys():
            response, flag = server_functions.\
                             AVAILABLE_FUNCTIONS[uri](request.get_params())
            self._client.send(response.build_response())
            return flag

        result = self._check_status_errors(request)
        if result == -1:
            return False
        elif result == 1:
            return True

        full_file_path = self._get_full_path(request)

        requested_file = open(full_file_path, "r")
        data = requested_file.read()
        requested_file.close()

        headers = HTTPHeaders.HTTPHeaders()
        public_response_functions.add_default_headers(headers)
        headers["Content-Length"] = str(len(data))

        response = HTTPResponse.HTTPResponse(version=1.0, status_code=200,
                                             phrase="OK", headers=headers)
        self._client.send(response.build_response() + data)
        return True

    def _check_status_errors(self, request):
        """
        given an HTTPRequest checks for various status errors
        and sends them to the client if necessary. For example:
        if the client tries to access a restricted folder error 403
        will be sent.
        :param request:
        :return: 1 if an error was sent and the server shouldn't terminate
                 connection 0 if no errors were sent and -1 in case
                 the server should close the connection with the client
        """
        if request.get_method() not in SUPPORTED_METHODS:
            if DEBUG_LEVEL >= 0:
                print "Unsupported request method: {}".format(request.get_method())
            # send code 405
            response = HTTPResponse.HTTPResponse(version=1.0, status_code=405,
                                                 phrase="Method Not Allowed")
            headers = HTTPHeaders.HTTPHeaders()
            public_response_functions.add_default_headers(headers)
            headers["Content-Length"] = "0"
            response.set_headers(headers)
            self._client.send(response.build_response())
            return -1

        full_file_path = self._get_full_path(request)
        # check if the root abs path is the first substring at the
        # start, if not send forbidden response
        if self._is_restricted(full_file_path):
            if DEBUG_LEVEL >= 0:
                print "Client tried to access {} which is restricted".format(full_file_path)
            self._client.send(self._get_restricted_error())
            return 1

        if not path.isfile(full_file_path):
            if DEBUG_LEVEL >= 0:
                print "File: {} not found".format(full_file_path)
            # send 404 Not Found response
            self._client.send(self._get_404_response())
            return 1

        return 0

    def _get_full_path(self, request):
        """
        Given HTTPRequest returns a real path to the requested
        file. If the url is / substitutes it for index.html
        :param request: HTTPRequest
        :return: a real path to the requested file
        """
        # get rid of the preceding /
        url = request.get_uri()[1:] if request.get_uri()[0] == "/" else \
            request.get_uri()

        # if url is / change to index.html
        url = "index.html" if url == "" else url

        full_file_path = path.join(self._root, url)
        full_file_path = path.realpath(full_file_path)

        return full_file_path

    def _is_restricted(self, real_path):
        """
        given a full real path of a file or directory, checks if the file
        is in a restricted area
        :param real_path:
        :return:
        """
        if real_path.find(self._root) != 0:
            return True

        # get rid of the root part plus the following /
        real_path = real_path[len(self._root)+1:]
        for folder in self._restricted_folders:
            if real_path.find(folder) == 0:
                return True

        return False

    def _get_404_response(self):
        """
        builds a typical 404 http response
        :return: an http not found response
        """
        response = HTTPResponse.HTTPResponse(version=1.0, status_code=404,
                                             phrase="Not Found")
        # try to open not_found.html if it exists and utilize it
        # for the message
        # in case opening the file was unsuccessful just create a quick
        # message
        try:
            file_path = path.join(self._root, NOT_FOUND)
            f = open(file_path, "r")
        except IOError:
            message = "<body><h1>Not Found</h1></body>"
            if DEBUG_LEVEL >= 2:
                print "File {} wasn't found in root"
        else:
            message = f.read()
            f.close()

        headers = HTTPHeaders.HTTPHeaders()
        public_response_functions.add_default_headers(headers)
        headers["Content-Length"] = str(len(message))
        headers["Content-Type"] = "text/html"
        response.set_headers(headers)

        response.set_data(message)

        return response.build_response()

    def _get_restricted_error(self):
        """
        builds a typical restricted file/path response
        :return:
        """
        response = HTTPResponse.HTTPResponse(version=1.0, status_code=403,
                                             phrase="Forbidden")
        headers = HTTPHeaders.HTTPHeaders()
        headers["Content-Type"] = "text/html"
        public_response_functions.add_default_headers(headers)

        response_body = "<html><body><h1>Forbidden</h1></body></html>"

        try:
            html_page = open(path.join(self._root, self._restricted_html))
        except IOError:
            if DEBUG_LEVEL >= 2:
                print "File {} wasn't found in root".format(self._restricted_html)
        else:
            response_body = html_page.read()

        headers["Content-Length"] = str(len(response_body))
        response.set_data(response_body)
        response.set_headers(headers)

        return response.build_response()


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
