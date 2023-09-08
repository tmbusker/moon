from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from django.db import models


class AuthUser(AbstractUser):
    """Djangoの指針に従ってUserを最初からカスタマイズする"""
    class Meta:
        db_table = 'cmm_authuser'
        verbose_name = _("authorization user")
        verbose_name_plural = _("authorization users")
        permissions = [
            ("download_csv_authuser", "Can download AuthUser CSV"),
            ("download_excel_authuser", "Can download AuthUser EXCEL"),
            ("upload_csv_authuser", "Can upload AuthUser CSV"),
        ]


class AuthGroup(Group):
    """Groupを継承、cmmサイトに表示するためだけ…"""
    class Meta:
        db_table = 'cmm_authgroup'
        verbose_name = _("authorization group")
        verbose_name_plural = _("authorization group")
        permissions = [
            ("download_csv_authgroup", "Can download AuthGroup CSV"),
            ("download_excel_authgroup", "Can download AuthGroup EXCEL"),
            ("upload_csv_authgroup", "Can upload AuthGroup CSV"),
        ]


class FlagChoices(models.IntegerChoices):
    ON = 1, 'On'
    OFF = 0, 'Off'
