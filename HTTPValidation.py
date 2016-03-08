"""
contains function that validate http requests and responses
There are are no validation for the data itself but for the
request line and headers
The functions in this file utilizes the regex module(hopefully it is allowed)
"""
import re
import constants


def validate_request_line(request_line):
    """
    Validates that a request line is a HTTP compliant request
    :param request_line: The request line of an http message
    :return:
    """
    pattern = re.compile("[A-Z]{3,7} [/a-zA-Z._\-0-9]+\??"
                         "[a-zA-Z._\-0-9=&]* HTTP/1\.[01]")
    return True if re.match(pattern, request_line) else False


def validate_request(request):
    """
    Validates that a HTTP message is a valid request
    :param request:
    :return:
    """
    if not validate_request_line(request):
        print "Request line invalid"
        return False

    string_index = request.find(constants.CRLF) + 2
    headers = request[string_index:]

    if not validate_headers(headers):
        print "Invalid headers"
        return False

    return True


def validate_headers(headers):
    """
    Checks if a string may represent valid headers
    :param headers:
    :return:
    """
    pattern = re.compile("^[a-zA-Z\-]+: [^\r\n]+\r\n")
    while True:
        if not re.match(pattern, headers):
            return False

        string_index = headers.find(constants.CRLF) + 2
        # we're at the end of the headers and there is no
        # empty line return False
        if string_index == len(headers) - 1:
            return False

        headers = headers[string_index:]

        # if there is an empty line next to the match return true
        if headers[:2] == constants.CRLF:
            break

    return True
