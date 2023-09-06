import logging
from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from cmm.csv.csv_downloader import CsvModelAdminDownloader, ExcelModelAdminDownloader


_logger = logging.getLogger(__name__)

# 定数の定義はmethod名と一致する必要がある
DOWNLOAD_CSV = 'download_csv'
DOWNLOAD_EXCEL = 'download_excel'


# pragma: no cover
class CsvDownloadMixin:
    """
    Csvダウンロードのベースクラス
    Django AdminSiteのModel Change List画面のActionリストに、CSVダウンロードとExcelダウンロードActionを追加する
    {opts.app_label}.{DOWNLOAD_CSV}_{opts.model_name}の権限有無により、各Actionの表示非表示をコントロールする
    """

    def get_actions(self, request):
        """Django admin list viewのアクションリストを取得する（アクションのプルダウンリスト）"""
        actions = super().get_actions(request)
        # pylint: disable = protected-access
        opts = self.model._meta
        if not request.user.has_perm(f'{opts.app_label}.{DOWNLOAD_CSV}_{opts.model_name}'):
            for action in [DOWNLOAD_CSV, DOWNLOAD_EXCEL]:
                if action in actions:
                    del actions[action]
        else:
            if getattr(self, DOWNLOAD_CSV, None) is not None and DOWNLOAD_CSV in actions:
                del actions[DOWNLOAD_CSV]
            elif getattr(self, DOWNLOAD_EXCEL, None) is not None and DOWNLOAD_EXCEL in actions:
                del actions[DOWNLOAD_EXCEL]

        return actions


@admin.display(description=_('download csv'))
def download_csv(model_admin, request, queryset) -> HttpResponse:
    """
    django admin site用csv download action
    使用例: admin.site.add_action(download_csv, DOWNLOAD_CSV)
    """

    downloader = CsvModelAdminDownloader(model_admin)
    _logger.info('Start to downloading %s', downloader.get_file_name())
    response = downloader.generateResponse(queryset)
    _logger.info('Start to downloading %s', downloader.get_file_name())
    return response


@admin.display(description=_('download excel'))
def download_excel(model_admin, request, queryset):
    """
    django admin site用csv download action
    ここのExcel出力はただCSVデータをExcel形式で出力するのみ、複雑なExcelファイルを出力するものではない。
    使用例: admin.site.add_action(download_excel, DOWNLOAD_EXCEL)
    """

    downloader = ExcelModelAdminDownloader(model_admin)
    _logger.info('Start to downloading %s', downloader.get_file_name())
    response = downloader.generateResponse(queryset)
    _logger.info('Start to downloading %s', downloader.get_file_name())
    return response
