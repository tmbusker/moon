import csv
from datetime import date, datetime
from enum import Enum, StrEnum, auto
from typing import List
from cmm.models import SimpleTable, VersionedTable


class CsvEncoding(StrEnum):
    UTF8 = auto()
    SJIS = auto()
    CP932 = auto()

    UTF_8 = 'utf-8'
    S_JIS = 's-jis'
    SHIFT_JIS = 'utf-8'


class CsvLogOutput(Enum):
    """ ログの出力先 """

    NONE = 0        # 保存しない
    CONSOLE = 1
    FILE = 2
    DATABASE = 3


class CsvBase:
    """
    CSVファイルのアップロードとダウンロード処理の共通ベースクラス、
    djangoのmodelクラスをCSV列にマッピングする
    """
    # 一回の読み書き行数、0の場合はCSVファイルを一括処理する。
    chunk_size: int = 1000
    encoding = CsvEncoding.UTF8
    dialect: type[csv.Dialect] = csv.excel
    csv_extension: str = '.csv'
    excel_extension: str = '.xlsx'
    date_format: str = '%Y/%m/%d'
    datetime_format: str = '%Y/%m/%d %H:%M:%S'
    log_output: CsvLogOutput = CsvLogOutput.DATABASE

    @property
    def model_name(self) -> str:
        plural_name: str = self.model._meta.verbose_name_plural
        return plural_name

    def get_csv_file_name(self) -> str:
        return self.model_name + self.csv_extension

    def get_excel_file_name(self) -> str:
        return self.model_name + self.excel_extension

    def get_csv_content_type(self):
        return f'text/csv; charset={self.encoding}'

    def get_model_fields(self):
        return {f.name: f.get_internal_type() for f in self.model._meta.get_fields() if f.concrete}

    def get_csv_field_names(self) -> List[str]:
        """ユーザー設定を想定、設定がない場合はテーブル定義より取得"""
        csv_fields = [f for f in self.get_model_fields().keys() if f != 'id']

        if issubclass(self.model, SimpleTable):
            exclude_fields = [f.name for f in SimpleTable._meta.get_fields()]
            csv_fields = [f for f in csv_fields if f not in exclude_fields]

        if issubclass(self.model, VersionedTable):
            exclude_fields = [f.name for f in VersionedTable._meta.get_fields()]
            csv_fields = [f for f in csv_fields if f not in exclude_fields]

        return csv_fields

    def get_csv_headers(self) -> List[str]:
        return self.csv_headers if hasattr(self, 'csv_headers') else self.get_csv_field_names()

    def generate_csv_data(self, queryset):
        offset = 0
        while True:
            chunk_queryset = queryset[offset:offset + self.chunk_size].values(*self.get_csv_field_names())
            if not chunk_queryset:
                break
            for row in chunk_queryset:
                yield [v.strftime(self.datetime_format) if isinstance(v, datetime) else
                       (v.strftime(self.date_format) if isinstance(v, date) else v) for (k, v) in row.items()]
            offset += self.chunk_size
