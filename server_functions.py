"""
All the functions in this file will be executed by the server,
if they're called through the request line. Parameters to the functions should
be passed through the get request(using a ? and an &).
All the functions will generate an appropriate HTTPResponse and should also return
a flag that will signify to the server if the connection should be closed.
The server calling code expects a tuple of the following form: (response, flag),
so keep that in mind when writing functions in this file.
Unused/Unknown parameters will be ignored.
The following example represents a uri that utilizes the function say_hello:
/say_hello?name=Michael
In the case the user(agent) sent something like this: /say_hello?name=Michael&&&foo=bar
all the empty parameters will be ignored as well as the foo parameter since
the function say_hello doesn't use it. However, in case the user forgot to add the parameter name
an error response will be returned and the connection will be closed.

AVAILABLE_FUNCTIONS is a dictionary where the keys are the functions name and
the values are the functions, again the caller expects that so don't screw up
the structure. All the functions that should be used by the client are in this dictionary.
"""
import HTTPResponse
import public_response_functions
import HTTPHeaders


def say_hello(request_parameters):
    """
    :type request_parameters: dict
    :param request_parameters: The request the client sent
    :rtype: tuple
    :return: A tuple consisting of a response object(HTTPResponse), and a boolean
             signifies whether the server should close the connection with the client
             or continue to its next request
    """
    name_param = "name"
    if name_param not in request_parameters.keys():
        return public_response_functions.get_500_response("Parameter \"{}\""
                                                          " missing".format(name_param)), False

    hello_string = "Hello {}".format(request_parameters[name_param])
    response = HTTPResponse.HTTPResponse(version=1.0, status_code=200, phrase="OK",
                                         data=hello_string)
    headers = HTTPHeaders.HTTPHeaders()
    public_response_functions.add_default_headers(headers)
    headers["Content-Length"] = str(len(hello_string))

    response.set_headers(headers)

    return response, True

AVAILABLE_FUNCTIONS = {"say_hello": say_hello}
