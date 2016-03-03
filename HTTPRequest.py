"""

"""

import constants
import HTTPHeaders


class HTTPRequest(object):
    def __init__(self, request_line="", headers="", debug=0):
        """
        :param request_line: if "" _parse_request_line won't be called
        :param headers:may be a string or HTTPHeaders
        :param debug:
        :return:
        may raise ValueError
        """
        self._method = ""
        self._version = ""
        self._url = ""

        try:
            self._headers = HTTPHeaders.HTTPHeaders(headers)
        except ValueError:
            raise

        self._debug = debug
        try:
            self._parse_request_line(request_line)
        except ValueError:
            raise

    def _parse_request_line(self, request_line):
        """
        :param request_line:
        :return:
        may throw ValueError
        """
        request_components = request_line.split(constants.SPACE)
        if self._debug:
            print request_components

        if len(request_components) != 3:
            raise ValueError("Unmatched components in request line: {}".format(request_line))

        self._method = request_components[0]

        self._url = request_components[1]

        # validate version
        version = request_components[2].split("/")
        if len(version) != 2:
            raise ValueError("Unknown version {}".format(request_components[2]))
        self._version = version

    def get_method(self):
        """
        :return:current value of member _method
        """
        return self._method

    def set_method(self, method):
        """
        Set for member _method
        :param method:string representing method
        :return:
        may throw type exception
        """
        if not isinstance(method, str):
            raise TypeError("Unexpected type {}".format(type(method)))
        self._method = method

    def get_version(self):
        """
        :return:current value of member _version1
        """
        return self._version

    def set_version(self, version):
        """
        :param version:
        :return:
        may throw TypeError if version isn't string
        """
        if not isinstance(version, str):
            raise TypeError("Unexpected type {}".format(type(version)))
        self._version = version

    def build_request(self):
        request_line = "{} {} {}{}".format(self._method, self._url,
                                           self._version, constants.CRLF)
        request = "{}{}".format(request_line, self._headers.build_headers())
        return request

    def get_headers(self):
        return self._headers

    def set_headers(self, headers):
        """
        :param headers:expected type-HTTPHeaders
        :return:
        """
        if not isinstance(headers, HTTPHeaders.HTTPHeaders):
            raise TypeError("Unecpected type: {} for headers".format(type(headers)))
        self._headers = headers

    def get_url(self):
        return self._url
