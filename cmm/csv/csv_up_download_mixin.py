from cmm.csv import CsvUploadMixin
from cmm.csv import CsvDownloadMixin


class CsvMixin(CsvUploadMixin, CsvDownloadMixin):
    """Csv UploadとDownloadをまとめたMixinクラス"""
