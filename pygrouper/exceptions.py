"""
Grouper API Exceptions
"""

class GrouperAPIException(Exception):
    """Base class for exceptions in this module."""
    pass

class GrouperAPIError(GrouperAPIException):
    """Exception for passing errors on to the calling application"""
    def __init__(self, message):
        self.message = message

class GrouperAPIRequestsException(GrouperAPIException):
    """Exception for wrapping errors thrown by the Requests module"""
    def __init__(self, message):
        self.message = message
