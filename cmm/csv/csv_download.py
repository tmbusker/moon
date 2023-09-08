import logging
import csv
from urllib.parse import quote
from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from xlsxwriter.workbook import Workbook
from cmm.csv import CsvBase
from cmm.logging import log_decorator


# 定数の定義はmethod名と一致する必要がある
DOWNLOAD_CSV = 'download_csv'
DOWNLOAD_EXCEL = 'download_excel'
_logger = logging.getLogger(__name__)


# pragma: no cover
class CsvDownloadMixin(CsvBase):
    """
    Csvダウンロードのベースクラス、admin.ModelAdminのMixin
    Django AdminSiteのModel Change List画面のActionリストに、CSVダウンロードとExcelダウンロードActionを追加する
    {opts.app_label}.{DOWNLOAD_CSV}_{opts.model_name}の権限有無により、各Actionの表示非表示をコントロールする
    """

    def get_actions(self, request):
        """CSVダウンロード権限がない場合、Django admin list viewのアクションリストから非表示にする"""
        actions = super().get_actions(request)
        # pylint: disable = protected-access
        opts = self.model._meta
        if not request.user.has_perm(f'{opts.app_label}.{DOWNLOAD_CSV}_{opts.model_name}'):
            if DOWNLOAD_CSV in actions:
                del actions[DOWNLOAD_CSV]
        return actions

    def generate_csv_response(self, queryset) -> HttpResponse:
        http_response = HttpResponse(content_type=self.get_csv_content_type())
        # quote()を使わないとファイル名がセットされない
        http_response['Content-Disposition'] = f'attachment; filename={quote(self.get_csv_file_name())}'

        writer = csv.writer(http_response, self.dialect)

        # ヘッダーを出力
        if self.get_csv_headers():
            writer.writerow(self.get_csv_headers())

        # CSVデータを出力
        for row in self.generate_csv_data(queryset):
            writer.writerow(row)

        return http_response


@admin.display(description=_('download csv'))
@log_decorator
def download_csv(model_admin, request, queryset) -> HttpResponse:
    """
    django admin site用csv download action
    使用例: admin.site.add_action(download_csv, DOWNLOAD_CSV)
    """
    file_name = model_admin.get_csv_file_name()
    _logger.info('%s download has started.', file_name)
    response = model_admin.generate_csv_response(queryset)
    _logger.info('%s download finished.', file_name)
    return response


# pragma: no cover
class ExcelDownloadMixin(CsvBase):
    """
    Excelダウンロードのベースクラス、admin.ModelAdminのMixin
    Django AdminSiteのModel Change List画面のActionリストに、CSVダウンロードとExcelダウンロードActionを追加する
    {opts.app_label}.{DOWNLOAD_EXCEL}_{opts.model_name}の権限有無により、各Actionの表示非表示をコントロールする
    """

    def get_actions(self, request):
        """EXCELダウンロード権限がない場合、Django admin list viewのアクションリストから非表示にする"""
        actions = super().get_actions(request)
        # pylint: disable = protected-access
        opts = self.model._meta
        if not request.user.has_perm(f'{opts.app_label}.{DOWNLOAD_EXCEL}_{opts.model_name}'):
            if DOWNLOAD_EXCEL in actions:
                del actions[DOWNLOAD_EXCEL]
        return actions

    def generate_excel_response(self, queryset) -> HttpResponse:
        """ダウンロード内容を生成する"""
        file_name = self.get_excel_file_name()
        http_response = HttpResponse(content_type='application/vnd.ms-excel')
        # quote()を使わないとファイル名がセットされない
        http_response['Content-Disposition'] = f'attachment; filename={quote(file_name)}'

        workbook = Workbook(http_response, {'in_memory': True})
        worksheet = workbook.add_worksheet(self.model._meta.model_name)

        row_num = 0

        # ヘッダー行の出力
        csv_headers = self.get_csv_headers()
        if csv_headers is not None:
            for col_num, value in enumerate(csv_headers):
                worksheet.write(row_num, col_num, value)
            row_num += 1

        # 内容出力
        for row in self.generate_csv_data(queryset):
            for col_num, value in enumerate(row):
                worksheet.write(row_num, col_num, value)
            row_num += 1

        workbook.close()

        return http_response


@admin.display(description=_('download excel'))
def download_excel(model_admin, request, queryset):
    """
    django admin site用excel download action
    ここのExcel出力はただCSVデータをExcel形式で出力するのみ、複雑なExcelファイルを出力するものではない。
    使用例: admin.site.add_action(download_excel, DOWNLOAD_EXCEL)
    """

    file_name = model_admin.get_excel_file_name()
    _logger.info('Start to downloading %s', file_name)
    response = model_admin.generate_excel_response(queryset)
    _logger.info('Start to downloading %s', file_name)
    return response
