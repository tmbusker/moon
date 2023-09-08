from cmm.csv import CsvDownloadMixin, ExcelDownloadMixin, CsvUploadMixin


class CsvMixin(CsvDownloadMixin, ExcelDownloadMixin, CsvUploadMixin):
    """Csv UploadとDownloadをまとめたMixinクラス"""
