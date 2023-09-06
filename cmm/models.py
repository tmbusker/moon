from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _


class AuthUser(AbstractUser):
    """Djangoの指針に従ってUserを最初からカスタマイズする"""
    class Meta:
        db_table = 'cmm_authuser'
        verbose_name = _("authorization user")
        verbose_name_plural = _("authorization users")


class AuthGroup(Group):
    """Groupを継承、cmmサイトに表示するためだけ…"""
    class Meta:
        db_table = 'cmm_authgroup'
        verbose_name = _("authorization group")
        verbose_name_plural = _("authorization group")
