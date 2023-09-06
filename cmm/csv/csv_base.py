import csv
from enum import Enum, StrEnum, auto


class CsvEncoding(StrEnum):
    UTF8 = auto()
    SJIS = auto()
    CP932 = auto()

    UTF_8 = 'utf-8'
    S_JIS = 's-jis'
    SHIFT_JIS = 'utf-8'


class LogLocation(Enum):
    """ ログの出力先 """

    NONE = 0        # 保存しない
    CONSOLE = 1
    FILE = 2
    DATABASE = 3


class CsvBase:
    """
    CSVファイルのアップロードとダウンロード処理の共通ベースクラス、
    djangoのmodelクラスをCSV列にマッピングする
    ModelAdminへのMixinを想定する
    """

    def __init__(self) -> None:
        self._chunk_size: int = 1000

        self.encoding = CsvEncoding.UTF8
        self.dialect: type[csv.Dialect] = csv.excel
        self.file_extension: str = '.csv'
        self.date_format: str = '%Y/%m/%d'
        self.log_location: LogLocation = LogLocation.FILE

    @property
    def chunk_size(self) -> int:
        """
        一回の読み書き行数、chunkごとにCSVファイル読込または保存処理を実行する。
        0の場合はCSVファイルをchunkごとに分割することなく一括処理する。
        """
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: int):
        if value >= 0:
            self._chunk_size = value
        else:
            raise ValueError()
