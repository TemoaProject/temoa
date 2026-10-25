from _typeshed import Incomplete
from pyomo.common.download import DownloadFactory as DownloadFactory
from pyomo.common.download import FileDownloader as FileDownloader
from pyomo.scripting.pyomo_parser import add_subparser as add_subparser

class GroupDownloader:
    downloader: Incomplete
    def __init__(self) -> None: ...
    def create_parser(self, parser): ...
    def call(self, args, unparsed): ...
