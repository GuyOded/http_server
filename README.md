Currently the server supports the method get only.
The server doesn't support http parameters.
If an error occurred while interpreting a request, an erroneous response will be returned, the connection
will be closed.
In case the uri is empty the index.html in root directory will be returned in the response.
If index html isn't present in the root directory a the server will respond with a 404 message.
