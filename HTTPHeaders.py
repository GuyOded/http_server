"""
This class handles the headers of an http request/response.
Given the headers part the class will parse it and create
a dictionary of the format: header:value.
Headers may be added or changed.
The method build_headers will return a string of all the headers
according to the http format: "header1: blabla\r\nlast-header: blabla\r\n\r\n"
"""
import constants


class HTTPHeaders(object):
    def __init__(self, headers="", debug=0):
        """
        :param debug: For debugging purposes
        :param headers: The headers part of a particular http request or response.
                        For example: Connection: close\r\n
                                     Content-Type: text/plain\r\n
                                     \r\n
                        This parameter is optional, in case the user
                        wishes to fill in the headers later on after construction
        """
        self._debug = debug
        if not isinstance(headers, str):
            raise TypeError("Got {} but expected {}".format(type(headers), str))
        self._headers = {}
        if headers:
            try:
                self._parse_headers(headers)
            except ValueError:
                raise

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("Got {} but expected {}".format(type(key), str))
        if not isinstance(value, str):
            raise TypeError("Got {} but expected {}".format(type(value), str))

        self._headers[key] = value

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError("Got {} but expected {}".format(type(key), str))

        return self._headers[key]

    def _parse_headers(self, headers_string):
        """
        extract the headers from the given parameter and creates new
        entries in the dictionary. The string must be a valid headers
        string
        :return: None
        """
        headers_list = headers_string.split(constants.CRLF)
        if self._debug:
            print headers_list

        # filter unnecessary empty elements
        headers_list = filter(lambda s: s != "", headers_list)

        for header in headers_list:
            header_field_list = header.split(constants.COLON)

            # check header structure
            if len(header_field_list) < 2:
                raise ValueError("Expected colon in {}".format(header_field_list))

            field_name, header_value = header_field_list[0], header_field_list[1]
            # space after colon
            if header_value[0] != constants.SPACE:
                raise ValueError("Expected space after colon \
                                 in header: {}:{}".format(field_name, header_value))

            self._headers[field_name] = header_value[1:]

        if self._debug:
            print self._headers

    def build_headers(self):
        """
        builds a string comprising of the headers in the dictionary member
        if self._headers = {"Connection": "keep-alive", "Content-Encoding": "base64"}
        the result will be: "Connection: keep-alive\r\nContent-Encoding: base64\r\n\r\n"
        :return:
        """
        result = ""
        for key in self._headers.keys():
            result += "{}: {}{}".format(key, self._headers[key], constants.CRLF)

        return result + constants.CRLF
