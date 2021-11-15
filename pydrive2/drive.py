from .apiattr import ApiAttributeMixin
from .gdrivefile import GoogleDriveFile # import from drive file not using default package
from .gdrivefile import GoogleDriveFileList
from .dropboxfile import DropboxFile # import from drive file not using default package
from .dropboxfile import DropboxFileList # import from drive file not using default package
#from .onedrivefile import OnedriveFile # import from drive file not using default package
# from .onedrivefile import OnedriveFileList # import from drive file not using default package
import requests



from .auth import LoadAuth


class GoogleDrive(ApiAttributeMixin, object):
    """Main Google Drive class."""

    startPageToken=None
    def __init__(self, auth=None):
        """Create an instance of GoogleDrive.

    :param auth: authorized GoogleAuth instance.
    :type auth: pydrive2.auth.GoogleAuth.
    """
        ApiAttributeMixin.__init__(self)
        self.auth = auth
        print("getting start page token")
        headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}
        response = requests.get("https://www.googleapis.com/drive/v3/changes/startPageToken",headers=headers).json()
        self.startPageToken = response['startPageToken']

    def CreateFile(self, metadata=None):
        """Create an instance of GoogleDriveFile with auth of this instance.

    This method would not upload a file to GoogleDrive.

    :param metadata: file resource to initialize GoogleDriveFile with.
    :type metadata: dict.
    :returns: pydrive2.files.GoogleDriveFile -- initialized with auth of this
              instance.
    """
        return GoogleDriveFile(auth=self.auth, metadata=metadata)

    def ListFile(self, param=None):
        """Create an instance of GoogleDriveFileList with auth of this instance.

    This method will not fetch from Files.List().

    :param param: parameter to be sent to Files.List().
    :type param: dict.
    :returns: pydrive2.files.GoogleDriveFileList -- initialized with auth of
              this instance.
    """
        return GoogleDriveFileList(auth=self.auth, param=param)

    @LoadAuth
    def GetAbout(self):
        """Return information about the Google Drive of the auth instance.

    :returns: A dictionary of Google Drive information like user, usage, quota etc.
    """
        return self.auth.service.about().get().execute(http=self.http)

class DropboxDrive(ApiAttributeMixin, object):
    """Main Dropbox  class."""


    startPageToken=None
    def __init__(self, auth=None):
        """Create an instance of GoogleDrive.

    :param auth: authorized GoogleAuth instance.
    :type auth: pydrive2.auth.GoogleAuth.
    """
        ApiAttributeMixin.__init__(self)
        self.auth = auth
        import requests
        import json
        url = "https://api.dropboxapi.com/2/files/list_folder/get_latest_cursor"
        headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}
        data = {
            "path": ""
        }
        r = requests.post(url, headers=headers, data=json.dumps(data))
        self.startPageToken=r.json()['cursor']

    def CreateFile(self, metadata=None):
        """Create an instance of GoogleDriveFile with auth of this instance.

    This method would not upload a file to GoogleDrive.

    :param metadata: file resource to initialize GoogleDriveFile with.
    :type metadata: dict.
    :returns: pydrive2.files.GoogleDriveFile -- initialized with auth of this
              instance.
        """
        return DropboxFile(auth=self.auth, metadata=metadata)

    def ListFile(self, param=None):
        """Create an instance of GoogleDriveFileList with auth of this instance.

    This method will not fetch from Files.List().

    :param param: parameter to be sent to Files.List().
    :type param: dict.
    :returns: pydrive2.files.GoogleDriveFileList -- initialized with auth of
              this instance.
    """
        return DropboxFileList(auth=self.auth, param=param)

    @LoadAuth
    def GetAbout(self):
        """Return information about the Google Drive of the auth instance.

    :returns: A dictionary of Google Drive information like user, usage, quota etc.
    """
        return self.auth.service.about().get().execute(http=self.http)

class OneDrive(ApiAttributeMixin, object):
    """Main Dropbox  class."""

    def __init__(self, auth=None):
        """Create an instance of GoogleDrive.

    :param auth: authorized GoogleAuth instance.
    :type auth: pydrive2.auth.GoogleAuth.
    """
        ApiAttributeMixin.__init__(self)
        self.auth = auth

    def CreateFile(self, metadata=None):
        """Create an instance of GoogleDriveFile with auth of this instance.

    This method would not upload a file to GoogleDrive.

    :param metadata: file resource to initialize GoogleDriveFile with.
    :type metadata: dict.
    :returns: pydrive2.files.GoogleDriveFile -- initialized with auth of this
              instance.
    """
        return OnedriveFile(auth=self.auth, metadata=metadata)

    def ListFile(self, param=None):
        """Create an instance of GoogleDriveFileList with auth of this instance.

    This method will not fetch from Files.List().

    :param param: parameter to be sent to Files.List().
    :type param: dict.
    :returns: pydrive2.files.GoogleDriveFileList -- initialized with auth of
              this instance.
    """
        return OnedriveFileList(auth=self.auth, param=param)

    @LoadAuth
    def GetAbout(self):
        """Return information about the Google Drive of the auth instance.

    :returns: A dictionary of Google Drive information like user, usage, quota etc.
    """
        return self.auth.service.about().get().execute(http=self.http)
