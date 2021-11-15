from .auth import GoogleAuth
from .drive import GoogleDrive
from .drive import DropboxDrive
class Connector(object):
    """docstring for Connector"""
    def __init__(self):
        super(Connector, self).__init__()
    def get_con(self, bk=None,tk=None):
        gauth=GoogleAuth(access_token=tk)
        backends = {
        "Google": GoogleDrive,
        "Dropbox": DropboxDrive
        }
        return backends[bk](gauth)

