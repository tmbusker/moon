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

    list_display = ('file_name', 'row_no', 'csv_content', 'message', 'creator', 'created_at')

    # list_display_links = None       # remove the link to the model's edit view
    list_display_links = ('file_name', 'row_no', 'csv_content')
    list_per_page = 20
    search_fields = ['creator', 'created_at', 'log_type', 'log_level', 'file_name']
    list_filter = ('file_name', 'creator', 'created_at', 'log_type', 'log_level')

    def has_add_permission(self, request, obj=None):
        '''hide the add button'''
        # pylint: disable = unused-argument
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Add a custom button/link to the change view page
        extra_context = extra_context or {}
        extra_context['hide_delete_link'] = True
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False

        return super().change_view(
            request,
            object_id,
            form_url=form_url,
            extra_context=extra_context,
        )
