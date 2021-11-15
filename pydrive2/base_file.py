import io
import mimetypes
import json
from functools import wraps
from .apiattr import ApiAttribute
from .apiattr import ApiAttributeMixin
from .apiattr import ApiResource
from .apiattr import ApiResourceList
from .auth import LoadAuth
from abc import ABC, abstractmethod
def LoadMetadata(decoratee):
    """Decorator to check if the file has metadata and fetches it if not.

  :raises: ApiRequestError, FileNotUploadedError
  """

    @wraps(decoratee)
    def _decorated(self, *args, **kwargs):
        if not self.uploaded:
            self.FetchMetadata()
        return decoratee(self, *args, **kwargs)

    return _decorated
class DriveFile(ABC,ApiAttributeMixin, ApiResource):
    """Base Class for Drive File instance.

  Inherits ApiResource which inherits dict.
  Can access and modify metadata like dictionary.
  """

    content = ApiAttribute("content")
    uploaded = ApiAttribute("uploaded")
    metadata = ApiAttribute("metadata")
    access_token=""

    def __init__(self, auth=None, metadata=None, uploaded=False,token=""):
        """Create an instance of GoogleDriveFile.

    :param auth: authorized GoogleAuth instance.
    :type auth: pydrive2.auth.GoogleAuth
    :param metadata: file resource to initialize GoogleDriveFile with.
    :type metadata: dict.
    :param uploaded: True if this file is confirmed to be uploaded.
    :type uploaded: bool.
    """
        ApiAttributeMixin.__init__(self)
        ApiResource.__init__(self)
        self.access_token=token
        self.metadata = {}
        self.dirty = {"content": False}
        self.auth = auth
        self.uploaded = uploaded
        if uploaded:
            self.UpdateMetadata(metadata)
        elif metadata:
            self.update(metadata)
        self.has_bom = True

    def __getitem__(self, key):
        """Overwrites manner of accessing Files resource.

    If this file instance is not uploaded and id is specified,
    it will try to look for metadata with Files.get().

    :param key: key of dictionary query.
    :type key: str.
    :returns: value of Files resource
    :raises: KeyError, FileNotUploadedError
    """
        try:
            return dict.__getitem__(self, key)
        except KeyError as e:
            if self.uploaded:
                raise KeyError(e)
            if self.get("id"):
                self.FetchMetadata()
                return dict.__getitem__(self, key)
            else:
                raise FileNotUploadedError()
    def SetContentString(self, content, encoding="utf-8"):
        """Set content of this file to be a string.

    Creates io.BytesIO instance of utf-8 encoded string.
    Sets mimeType to be 'text/plain' if not specified.

    :param encoding: The encoding to use when setting the content of this file.
    :type encoding: str
    :param content: content of the file in string.
    :type content: str
    """
        print("base class")
        self.content = io.BytesIO(content.encode(encoding))
        if self.get("mimeType") is None:
            self["mimeType"] = "text/plain"
    @abstractmethod
    def FetchMetadata(self, fields=None, fetch_all=False):
        pass
    @abstractmethod
    def Upload(self, param=None):
        pass
    @abstractmethod
    @LoadMetadata
    def FetchContent(self, mimetype=None, remove_bom=False):
        pass
    def _WrapRequest(self, request):
        """Replaces request.http with self.http.
    Ensures thread safety. Similar to other places where we call
    `.execute(http=self.http)` to pass a client from the thread local storage.
    """
        if self.http:
            request.http = self.http
        return request


