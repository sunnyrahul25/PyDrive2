from .base_file import *
import requests
import os

class OnedriveFile(DriveFile):
    def FetchMetadata(self, fields=None, fetch_all=False):
        """Download file's metadata from id using Files.get().

    :param fields: The fields to include, as one string, each entry separated
                   by commas, e.g. 'fields,labels'.
    :type fields: str

    :param fetch_all: Whether to fetch all fields.
    :type fetch_all: bool

    :raises: ApiRequestError, FileNotUploadedError
    """
        print("package using only request api")
        file_id = self.metadata.get("id") or self.get("id")

        if fetch_all:
            fields = "*"

        if file_id:
            try:
                # replace with request python call 

                headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}

                response = requests.get("https://www.googleapis.com/drive/v3/files/"+file_id,params={'fields':'*'},headers=headers)
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
        headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}
        params = {
            "id": self.metadata.get("id")
        }
        # lets only test for images.
        file_id = self.metadata.get("id")
        r = requests.get(
            "https://www.googleapis.com/drive/v3/files/"+file_id,params = { 'alt' : 'media' },stream=True,
            headers=headers
        )
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
                # 1. Retrieve session for resumable upload.
                print(self.auth.access_token,"TOK")
                headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}
                params = self.GetChanges()
                print(params)
                params["supportsAllDrives"] = True
                r = requests.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
                    headers=headers,
                    data=json.dumps(params)
                )
                print(r.headers)
                location = r.headers['Location']
                # 2. Upload the file.
                filesize=self.content.getbuffer().nbytes
                headers = {"Content-Range": "bytes 0-" + str(filesize - 1) + "/" + str(filesize)}
                r = requests.put(location, headers=headers, data=self.content)
                metadata=r.json()
        except errors.HttpError as error:
            print("ERROR")
            #raise ApiRequestError(error)
        else:
            self.uploaded = True
            self.dirty["content"] = False
            self.UpdateMetadata(metadata)

class GoogleDriveFileList(ApiResourceList):
    """Google Drive FileList instance.

  Equivalent to Files.list() in Drive APIs.
  """

    def __init__(self, auth=None, param=None):
        """Create an instance of GoogleDriveFileList."""
        super(GoogleDriveFileList, self).__init__(auth=auth, metadata=param)

    # TODO: replace it with request call #
    def _GetList(self):
        """Overwritten method which actually makes API call to list files.

    :returns: list -- list of pydrive2.files.OnedriveFile.
    """
        changes = self["changes"]
        # print("chagnes",changes)
        # print("metadata",self["changes"])
        if  changes == None:
            headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}
            # lets only test for images.
            r = requests.get(
                "https://www.googleapis.com/drive/v3/files/",params = self.metadata,
                headers=headers
            )
            response=r.json()
            result = []
            for file_metadata in response["files"]:
                tmp_file = OnedriveFile(
                    auth=self.auth, metadata=file_metadata, uploaded=True
                )
                result.append(tmp_file)
            return result
        else:
            headers = {"Authorization": "Bearer "+self.auth.access_token, "Content-Type": "application/json"}
            r = requests.get(
                "https://www.googleapis.com/drive/v3/changes",params = {'pageToken':self["pageToken"]},
                headers=headers
            )
            response=r.json()
            result = []
            for file_metadata in response["changes"]:
                tmp_file = OnedriveFile(
                    auth=self.auth, metadata=file_metadata, uploaded=True
                )
                result.append(tmp_file)
            return result
