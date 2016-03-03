import HTTPHeaders
import constants


class HTTPResponse(object):
    def __init__(self, version=1.0, status_code=0,
                 phrase="", headers="", data=""):
        """

        :param version: The version of the http response (float) default is 1.0
        :param status_code: e.g 200, 404 etc. (int)
        :param phrase: A phrase that indicates what the status code means (Not Found, OK)
                       (str)
        :param headers: can be either HTTPHeaders or a valid string
        :param data: Consider this one an optional parameter. The user may not use this
                     one and then chain the data in its own code: build_reponse() + data
        """
        self._headers = HTTPHeaders.HTTPHeaders()
        self._version = 1.0
        self._phrase = ""
        self._status_code = 0
        self._data = data

        try:
            self.set_headers(headers)
            self.set_status_code(status_code)
            self.set_phrase(phrase)
            self.set_version(version)
        except Exception:
            raise

    def build_response(self):
        """
        builds an http response when called on an object
        :return: A string that is the full http response
        """
        status_line = "HTTP/{} {} {}{}".format(self._version,
                                               self._status_code,
                                               self._phrase, constants.CRLF)
        return status_line + self._headers.build_headers() + self._data

    def set_headers(self, headers):
        if isinstance(headers, str):
            try:
                self._headers = HTTPHeaders.HTTPHeaders(headers)
            except:
                raise
        elif isinstance(headers, HTTPHeaders.HTTPHeaders):
            self._headers = headers
        else:
            raise TypeError("Expeted types are {} or {}".format(str, HTTPHeaders.HTTPHeaders))

    def get_headers(self):
        return self._headers

    def set_version(self, version):
        if not isinstance(version, float):
            raise TypeError("Expected type is {}".format(float))

        self._version = version

    def get_version(self):
        return self._version

    def set_data(self, data):
        if not isinstance(data, str):
            raise TypeError("Expected type is {}".format(str))
        self._data = data

    def get_data(self):
        return self._data

    def set_status_code(self, status_code):
        if not isinstance(status_code, int):
            raise TypeError("Expected type is {}".format(int))
        self._status_code = status_code

    def get_status_code(self):
        return self._status_code

    def set_phrase(self, phrase):
        if not isinstance(phrase, str):
            raise TypeError("Expected type is {}".format(str))
        self._phrase = phrase

    def get_phrase(self):
        return self._phrase
