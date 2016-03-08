"""
Holds server related (and only server related) constants.
Other files may also use these constants e.g public_response_functions.py
"""


__all__ = ["SUPPORTED_METHODS", "NOT_FOUND", "RESTRICTED_HTML_PAGE"]


# The methods the server supports at the moment
SUPPORTED_METHODS = ["GET"]
# Not Found HTML file name, must be in root
NOT_FOUND = "not_found.html"
RESTRICTED_HTML_PAGE = "restricted.html"
