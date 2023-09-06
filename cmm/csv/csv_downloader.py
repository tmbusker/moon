from abc import ABC, abstractmethod
import csv
from datetime import date
from urllib.parse import quote
from django.http import HttpResponse
from django.contrib.admin import ModelAdmin
from xlsxwriter.workbook import Workbook

from cmm.csv import CsvModelAdmin


class CsvDownloader(ABC):
    """ダウンロードの共通処理をまとめたもの"""

    def __init__(self) -> None:
        self.http_response = HttpResponse(content_type=self.get_content_type())
        # quote()を使わないとファイル名がセットされない
        self.http_response['Content-Disposition'] = f'attachment; filename={quote(self.get_file_name())}'

    @abstractmethod
    def get_file_name(self) -> str:
        pass            # pragma: no cover

    @abstractmethod
    def get_content_type(self) -> str:
        pass            # pragma: no cover


class CsvModelAdminDownloader(CsvModelAdmin, CsvDownloader):
    """CSVファイルのダウンロード"""

    def __init__(self, model_admin: ModelAdmin) -> None:
        CsvModelAdmin.__init__(self, model_admin)
        CsvDownloader.__init__(self)

    def get_file_name(self) -> str:
        return self.model_name + self.file_extension

    def get_content_type(self):
        return f'text/csv; charset={self.encoding}'

    def generateResponse(self, queryset) -> HttpResponse:
        writer = csv.writer(self.http_response, self.dialect)

        # ヘッダーを出力
        if self.csv_headers:
            writer.writerow(self.csv_headers)

        # CSVデータを出力
        for row in queryset.values(*self.model_fields):
            # 日付型の出力フォーマットをセットする
            values = [v.strftime(self.date_format) if isinstance(v, date) else v for (k, v) in row.items()]
            writer.writerow(values)

        return self.http_response


class ExcelModelAdminDownloader(CsvModelAdmin, CsvDownloader):
    """Excelファイルのダウンロード"""

    def __init__(self, model_admin: ModelAdmin) -> None:
        CsvModelAdmin.__init__(self, model_admin)
        CsvDownloader.__init__(self)

    def get_file_name(self) -> str:
        return self.model_name + '.xlsx'

    def get_content_type(self):
        return 'application/vnd.ms-excel'

    def generateResponse(self, queryset) -> HttpResponse:
        """ダウンロード内容を生成する"""

        workbook = Workbook(self.http_response, {'in_memory': True})
        worksheet = workbook.add_worksheet(self.model_admin.model._meta.model_name)

        row_num = 0

        # ヘッダー行の出力
        if self.csv_headers is not None:
            for col_num, value in enumerate(self.csv_headers):
                worksheet.write(row_num, col_num, value)
            row_num += 1

        # 内容出力
        for row in queryset.values_list(*self.model_fields):
            for col_num, value in enumerate(row):
                worksheet.write(row_num, col_num, value)
            row_num += 1

        workbook.close()

        return self.http_response
