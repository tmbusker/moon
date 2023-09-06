import json
from typing import Any, List
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from cmm.models import SimpleTable


class CsvLogModelAdmin(admin.ModelAdmin):
    """
    CSVアップロード、ダウンロードのログをAdminSiteに表示する
    """

    list_display = ('creator', 'created_at', 'log_type', 'log_level', 'file_name',
                    'row_no', 'row_content', 'message')

    list_display_links = None       # remove the link to the model's edit view
    list_per_page = 20
    search_fields = ['creator', 'created_at', 'log_type', 'log_level', 'file_name']
    list_filter = ('file_name', 'creator', 'created_at', 'log_type', 'log_level')

    def has_add_permission(self, request, obj=None):
        '''hide the add button'''
        # pylint: disable = unused-argument
        return False
