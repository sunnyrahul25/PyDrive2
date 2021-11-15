from .base_file import *
import requests
import json
import os

class DropboxFile(DriveFile):
    def FetchMetadata(self, fields=None):
        """Download file's metadata from id using Files.get().

    :param fields: The fields to include, as one string, each entry separated
                   by commas, e.g. 'fields,labels'.
    :type fields: str

    :param fetch_all: Whether to fetch all fields.
    :type fetch_all: bool

    :raises: ApiRequestError, FileNotUploadedError
    """
        file_id = self.metadata.get("path") or self.get("path")
        if file_id:
            try:
                headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}
                args={"path": self.metadata.get("path")}
                response=requests.post("https://api.dropboxapi.com/2/files/get_metadata",data=json.dumps(args),headers=headers)
                metadata=response.json()
            except errors.HttpError as error:
                print("ERROR")
            else:
                self.uploaded = True
                self.UpdateMetadata(metadata)
        else:
            print("ERROR file not uploaded ")
    def Upload(self, param=None):
        """Upload/update file by choosing the most efficient method.

    :param param: additional parameter to upload file.
    :type param: dict.
    :raises: ApiRequestError
    """
        self._FilesInsert(param=param)

    def FetchContent(self, mimetype=None):
        url = "https://content.dropboxapi.com/2/files/download"
        headers = {
            "Authorization": "Bearer "+self.auth.access_token
        }
        args={"path": self.metadata.get("path_lower")}
        r = requests.post(url, headers=headers,params={"arg":json.dumps(args)})
        self.content = io.BytesIO(r.content)
        self.dirty["content"] = False
    def _FilesInsert(self, param=None):
        """Upload a new file using Files.insert().

    :param param: additional parameter to upload file.
    :type param: dict.
    :raises: ApiRequestError
    """
        try:
            if self.dirty["content"]:
                url = "https://content.dropboxapi.com/2/files/upload"
                headers = {
                    "Authorization": "Bearer "+self.auth.access_token,
                    "Content-Type": "application/octet-stream"
                }
                args={"path": self.metadata.get("path")}
                r = requests.post(url, headers=headers,params={"arg":json.dumps(args)},data=self.content)
                metadata=r.json()
        except errors.HttpError as error:
            print("ERROR")
            #raise ApiRequestError(error)
        else:
            self.uploaded = True
            self.dirty["content"] = False
            self.UpdateMetadata(metadata)

class DropboxFileList(ApiResourceList):
    """Google Drive FileList instance.

  Equivalent to Files.list() in Drive APIs.
  """

    def __init__(self, auth=None, param=None):
        """Create an instance of GoogleDriveFileList."""
        super(DropboxFileList, self).__init__(auth=auth, metadata=param)

    # TODO: replace it with request call #
    def __next__(self):
        """Make API call to list resources and return them.

    Auto updates 'pageToken' every time it makes API call and
    raises StopIteration when it reached the end of iteration.

    :returns: list -- list of API resources.
    :raises: StopIteration
    """
        if "cursor" in self and self["cursor"] is None:
            raise StopIteration
        result = self._GetList()
        # might need to change api call for other dropbox container
        self["cursor"] = self.metadata.get("cursor")
        return result


    def _GetList(self):
        """Overwritten method which actually makes API call to list files.

    :returns: list -- list of pydrive2.files.DropboxFile.
    """

        headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}
        try:
            changes = self["changes"]
        except KeyError as e:
            try:
                data = {"cursor": self["cursor"]}
                url = "https://api.dropboxapi.com/2/files/list_folder_continue"
            except KeyError:
                url = "https://api.dropboxapi.com/2/files/list_folder"
                data ={"path":""}
            r = requests.post(url,headers=headers,data=json.dumps(data))
            #print("r",r.__dict__)
            response=r.json()
            result = []
            for file_metadata in response["entries"]:
                tmp_file = DropboxFile(
                    auth=self.auth, metadata=file_metadata, uploaded=True
                )
                result.append(tmp_file)
            return result
