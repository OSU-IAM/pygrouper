"""
Methods for working with the Grouper WS API
"""

from .client import GrouperClient
from .exceptions import GrouperAPIError

import requests

class GrouperAPI(GrouperClient):
    def is_member(self, username, groupname):
        """ Returns True if user is in the group

        Inputs:
          username - username of user in question
          groupname - group name to query, ex: org:test:somegroup

        Returns True if user is in group, otherwise False
        """
        try:
            result = self._get(f"groups/{groupname}/members/{username}")
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        metadata = result['WsHasMemberLiteResult']['resultMetadata']

        if metadata['resultCode'] == 'IS_MEMBER':
            return True
        elif 'resultCode2' in metadata and metadata['resultCode2'] == 'SUBJECT_NOT_FOUND':
            raise(GrouperAPIError('is_member - SUBJECT_NOT_FOUND error, is this user in Grouper?'))
        elif metadata['resultCode'] == 'IS_NOT_MEMBER':
            return False
        else:
            raise(GrouperAPIError(f"is_member - Unexpected result received: {metadata['resultCode']}"))

    def get_members(self, groupname):
        """ Retrieve members of a group

        Inputs:
          groupname - group name to query, ex: org:test:somestem

        Returns a list of subjects
        """
        try:
            result = self._get(f"groups/{groupname}/members")
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        metadata = result['WsGetMembersLiteResult']['resultMetadata']

        if metadata['resultCode'] == 'SUCCESS':
            if 'wsSubjects' in result['WsGetMembersLiteResult']:
                return result['WsGetMembersLiteResult']['wsSubjects']
            else:
                return []
        else:
            raise(GrouperAPIError(f"get_members - Unexpected result received: {metadata['resultCode']}"))

    def add_member(self, username, groupname):
        """ Add user as member to group

        Inputs:
          username - username of user to add
          groupname - target group name, ex: org:test:somegroup

        Returns True on success, otherwise raises GrouperAPIError
        """
        try:
            result = self._put(f"groups/{groupname}/members/{username}")
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        metadata = result['WsAddMemberLiteResult']['resultMetadata']

        if metadata['resultCode'] == 'SUCCESS':
            return True
        else:
            raise(GrouperAPIError(f"add_member - Unexpected result received: {metadata['resultCode']}"))

    def find_groups_by_stem(self, stem):
        """ Retrieve child groups associated with a stem

        Inputs:
          stem - stem name, ex: org:test:somestem

        Returns a list of groups
        """
        params = {
            'WsRestFindGroupsRequest': {
                'wsQueryFilter': {
                    'queryFilterType': 'FIND_BY_STEM_NAME',
                    'stemName': stem
                }
            }
        }
        try:
            result = self._post('groups', params)
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        metadata = result['WsFindGroupsResults']['resultMetadata']

        if metadata['resultCode'] == 'SUCCESS':
            if 'groupResults' in result['WsFindGroupsResults']:
                return result['WsFindGroupsResults']['groupResults']
            else:
                return []
        else:
            raise(GrouperAPIError(f"find_groups_by_stem - Unexpected result received: {metadata['resultCode']}"))

    def find_groups_by_name(self, groupname, exact=None):
        """ Retrieve groups by name

        Inputs:
          groupname - group name or substring to search for
          exact - (optional) boolean True to search for exact groupname match

        Returns a list of groups
        """
        if exact == True:
            query_filter_type = 'FIND_BY_GROUP_NAME_EXACT'
        else:
            query_filter_type = 'FIND_BY_GROUP_NAME_APPROXIMATE'

        params = {
            'WsRestFindGroupsRequest': {
                'wsQueryFilter': {
                    'queryFilterType': query_filter_type,
                    'groupName': groupname
                }
            }
        }
        try:
            result = self._post('groups', params)
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        metadata = result['WsFindGroupsResults']['resultMetadata']

        if metadata['resultCode'] == 'SUCCESS':
            if 'groupResults' in result['WsFindGroupsResults']:
                return result['WsFindGroupsResults']['groupResults']
            else:
                return []
        else:
            raise(GrouperAPIError(f"find_groups_by_name - Unexpected result received: {metadata['resultCode']}"))

    def delete_groups(self, groupnames):
        """ Delete groups

        Inputs:
          groupnames - list of group names to delete,
                       ex: ['org:test:somegroup1', 'org:test:somegroup2']

        Returns True on success, otherwise raises GrouperAPIError
        """
        if not len(groupnames) > 0:
            raise(GrouperAPIError(f"delete_groups - No group names provided"))

        params = {
            'WsRestGroupDeleteRequest': {
                'wsGroupLookups': []
            }
        }
        for group in groupnames:
            params['WsRestGroupDeleteRequest']['wsGroupLookups'].append({'groupName': group})
        try:
            result = self._post('groups', params)
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        metadata = result['WsGroupDeleteResults']['resultMetadata']

        if metadata['resultCode'] == 'SUCCESS':
            return True
        else:
            raise(GrouperAPIError(f"delete_groups - Unexpected result received: {metadata['resultCode']}"))

    def create_composite_group(self, *, leftgroup, rightgroup,
                               composite_type, description, newname):
        """ Create a composite group

        Inputs:
          leftgroup - lefthand group name, ex: org:test:somegroup1
          rightgroup - righthand group name, ex: org:test:somegroup2
          composite_type - type of composite group, must be 'complement', 'intersection', 'union'
          description - description of group
          newname - name of the group to create, ex: org:test:newgroup

        Returns True on success, otherwise raises GrouperAPIError
        """
        if composite_type not in ['complement', 'intersection', 'union']:
            raise(GrouperAPIError(f"create_composite_group - Invalid composite_type '{composite_type}'"))

        params = {
            'WsRestGroupSaveRequest': {
                'wsGroupToSaves': [
                    {
                        'wsGroup': {
                            'description': description,
                            'displayExtension': description,
                            'detail': {
                                'compositeType': composite_type,
                                'hasComposite': 'T',
                                'leftGroup': {
                                    'name': leftgroup
                                },
                                'rightGroup': {
                                    'name': rightgroup
                                }
                            },
                            'name': newname
                        },
                        'wsGroupLookup': {
                            'groupName': newname
                        }
                    }
                ]
            }
        }

        try:
            result = self._post('groups', params)
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        metadata = result['WsGroupSaveResults']['resultMetadata']

        if metadata['resultCode'] == 'SUCCESS':
            return True
        else:
            errmsg = (
                'create_composite_group - '
                f"Unexpected result received: {metadata['resultCode']}")
            raise(GrouperAPIError(errmsg))

    def add_privilege(self, *, accessgroup, targetgroup, privileges):
        """Add privilege for a group to access target group

        Inputs:
          accessgroup - name of group to give access to, ex: org:users:adminusers
          targetgroup - name of group to add privilege on, ex: org:test:somegroup
          privileges - single string, or list of strings of allowed values:
                       'read', 'view', 'update', 'admin', 'optin', 'optout'

        Returns True on success, otherwise raises GrouperAPIException
        """
        if isinstance(privileges, str):
            privileges = [privileges]
        for privilege in privileges:
            if privilege not in ['read', 'view', 'update', 'admin', 'optin', 'optout']:
                raise(GrouperAPIException(f"add_privilege - Invalid privilege name: {privilege}"))

        ags = self.find_groups_by_name(accessgroup, True)
        if len(ags):
            accessgroup_detail = ags.pop()
        else:
            raise(GrouperAPIException(f"add_privilege - Couldn't find access group: {accessgroup}"))

        params = {
            'WsRestAssignGrouperPrivilegesLiteRequest':{
                'allowed': 'T',
                'subjectId': accessgroup_detail['uuid'],
                'privilegeName': '',
                'groupName': targetgroup,
                'privilegeType': 'access'
            }
        }

        for privilege in privileges:
            params['WsRestAssignGrouperPrivilegesLiteRequest']['privilegeName'] = privilege
            try:
                result = self._post('grouperPrivileges', params)
            except requests.exceptions.HTTPError as err:
                raise(GrouperAPIError(err))
            metadata = result['WsAssignGrouperPrivilegesLiteResult']['resultMetadata']

            if metadata['resultCode'] not in ['SUCCESS_ALLOWED', 'SUCCESS_ALLOWED_ALREADY_EXISTED']:
                errmsg = (
                    'add_privilege - '
                    f"Unexpected result received: {metadata['resultCode']}")
                raise(GrouperAPIError(errmsg))

        return True
