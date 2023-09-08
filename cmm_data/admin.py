from django.contrib import admin

from cmm.csv import (download_csv, download_excel, DOWNLOAD_CSV, DOWNLOAD_EXCEL, CsvMixin)
from busking.admin import buskingSite
from cmm_data.models import Shikuchoson, Postcode


class ShikuchosonAdmin(CsvMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    header_row_number = 0
    list_display = ('shikuchoson_code', 'todofuken_name', 'shikuchoson_name')
    list_display_links = None       # remove the link to the model's edit view


class PostcodeAdmin(CsvMixin, admin.ModelAdmin):
    """AdminSiteでの表示をカスタマイズする"""
    header_row_number = 0
    chunk_size = 10000
    # encoding = 'SJIS'
    list_display = ('postcode', 'todofuken_name', 'shikuchoson_name', 'choiki_name')
    list_display_links = None       # remove the link to the model's edit view


buskingSite.add_action(download_csv, DOWNLOAD_CSV)
buskingSite.add_action(download_excel, DOWNLOAD_EXCEL)

buskingSite.register(Shikuchoson, ShikuchosonAdmin)
buskingSite.register(Postcode, PostcodeAdmin)
