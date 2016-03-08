"""
contains functions that build general responses
"""

import HTTPResponse
import HTTPHeaders
import server_constants


def get_error_response():
    """
    builds a typical http internal error response
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
    headers["Allow"] = ", ".join(server_constants.SUPPORTED_METHODS)
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


def get_500_response(message):
    """
    More or less the same as get_error_response, except that it returns an HTTPResponse
    object and you may also add a little text/plain message in the parameter.
    :type message: str
    :param message: the parameter will be added at the end of the response as its body
    :rtype: HTTPResponse.HTTPResponse
    :return:
    """
    headers = HTTPHeaders.HTTPHeaders()
    add_default_headers(headers)
    headers["Connection"] = "close"
    headers["Content-Length"] = str(len(message))
    headers["Content-Type"] = "text/plain"

    return HTTPResponse.HTTPResponse(version=1.0, status_code=500, phrase="Internal Error",
                                     headers=headers, data=message)
