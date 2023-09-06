from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.contrib.auth.admin import GroupAdmin, UserAdmin

from cmm.admin import SuperUserAdminSite
from cmm.models import AuthUser, AuthGroup
from cmm.csv import (download_csv, download_excel, DOWNLOAD_CSV, DOWNLOAD_EXCEL, CsvMixin)


class AuthUserAdmin(CsvMixin, UserAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    # inlines = (EmployeeInline,)


class AuthGroupAdmin(CsvMixin, GroupAdmin):
    """AdminSiteでの表示をカスタマイズする"""


class BuskingAdminSite(SuperUserAdminSite):
    """ AdminSiteのカスタマイズ"""
    site_title = _('busking site')          # displayed at the browser tab
    site_header = _('busking header')       # ようこその前に来るヘッダー
    # site_url = None

    index_title = _('busking index')

    def index(self, request):
        context = {
            **self.each_context(request),
            'title': _('busking'),          # アプリタイトル
            'app_list': self.get_app_list(request),
        }

        return render(request, 'admin/index.html', context=context)


# override default admin site
buskingSite = BuskingAdminSite(name='buskingSite')

buskingSite.add_action(download_csv, DOWNLOAD_CSV)
buskingSite.add_action(download_excel, DOWNLOAD_EXCEL)

buskingSite.register(AuthUser, AuthUserAdmin)
buskingSite.register(AuthGroup, AuthGroupAdmin)
