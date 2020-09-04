"""
A simple Python 3 client for working with the Grouper WS API
"""

from .api import GrouperAPI
from .exceptions import (
    GrouperAPIException, GrouperAPIError, GrouperAPIRequestsException
)
