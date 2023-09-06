import logging

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import FileField, Form
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse_lazy
from django.utils.translation import gettext_lazy as _
from cmm.csv import CsvLog, CsvUploader


UPLOAD_CSV = 'upload_csv'
_logger = logging.getLogger(__name__)


class CsvUploadForm(Form):
    """CSVファイルアップロード用Form"""
    upload_file = FileField(
        required=True,
        label=_('File to upload')
    )


class CsvUploadMixin:
    """
    CSVアップロード処理のDjango権限設定と画面処理
    """

    # change_list_template = 'cmm/change_list_with_csv_upload.html'
    upload_template = 'cmm/csv_upload.html'

    def has_upload_csv_permission(self, request) -> bool:
        """CSV upload権限有無のチェック"""
        opts = self.model._meta              # type: ignore[attr-defined]
        if opts.model_name.lower() == 'user' or opts.model_name.lower() == 'group':
            return request.user.has_perm(f'{opts.app_label}.add_{opts.model_name}')         # type:ignore[no-any-return]

        return request.user.has_perm(f'{opts.app_label}.{UPLOAD_CSV}_{opts.model_name}')    # type:ignore[no-any-return]

    def changelist_view(self, request, extra_context=None):
        """CSV upload権限を画面側に渡す"""
        extra_context = extra_context or {}
        extra_context['has_upload_csv_permission'] = self.has_upload_csv_permission(request)
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        """CSV uploadのURLを設定"""
        # pylint: disable = protected-access
        opts = self.model._meta
        upload_url = [
            path('csv_upload/', self.admin_site.admin_view(self.upload_action),
                 name=f'{opts.app_label}_{opts.model_name}_csv_upload'),
        ]
        return upload_url + super().get_urls()

    @transaction.non_atomic_requests
    def upload_action(self, request):
        """CSV upload処理"""
        if not self.has_upload_csv_permission(request):
            _logger.info('Trying to upload CSV file without permission.')
            raise PermissionDenied

        # pylint: disable = protected-access
        opts = self.model._meta
        title = _('Upload %(name)s') % {'name': opts.verbose_name}
        context = {
            **self.admin_site.each_context(request),
            'title': title,
            'app_list': self.admin_site.get_app_list(request),
            'opts': opts,
            'has_view_permission': self.has_view_permission(request),
        }

        # インポートファイルの選択画面表示
        if request.method == "GET":
            form = CsvUploadForm()

        # 画面で選択したインポートファイルの受け取り
        if request.method == "POST":
            form = CsvUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['upload_file']     # django.core.files.uploadedfile.InMemoryUploadedFile
                _logger.info('Importing CSV file %s into %s.', csv_file.name, opts.model_name)

                uploader = CsvUploader(self)

                # インポートファイルの読み込み処理
                (row_cnt, lot_number) = uploader.read_csv_file(csv_file, request.user.username)

                # ログ情報収集
                queryset = CsvLog.objects.filter(lot_number=lot_number)
                # 読み飛ばしたレコード
                skipped = list(queryset.filter(log_level=CsvLog.WARN).order_by('row_no'))
                # エラーで破棄したレコード
                discarded = list(queryset.filter(log_level=CsvLog.ERROR).order_by('row_no'))
                uploaded = row_cnt - uploader.header_row_number - len(skipped) - len(discarded)
                info = _('Upload result: uploaded %(imp)s rows, skipped %(skip)s rows and discarded: %(dis)s rows.'
                         ) % {'imp': uploaded, 'skip': len(skipped), 'dis': len(discarded)}
                _logger.info(info)

                if discarded or skipped:
                    context['title'] = _('%(name)s upload errors') % {'name': opts.verbose_name}
                    context['field_names'] = uploader.csv_headers
                    context['csv_logs'] = [csv_log.convert_content2values() for csv_log in discarded] \
                        + [csv_log.convert_content2values() for csv_log in skipped]
                    context['info'] = info
                    return TemplateResponse(request, 'cmm/csv_upload_error.html', context)

                return redirect(reverse_lazy(
                    f'{request.resolver_match.namespace}:{opts.app_label}_{opts.model_name}_changelist'))

        context['form'] = form
        return TemplateResponse(request, 'cmm/csv_upload.html', context)
