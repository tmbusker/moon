from django.contrib.admin import ModelAdmin
from cmm.csv import CsvDownloadMixin
from cmm.models import AuthUser


class AuthUserModelAdmin(ModelAdmin):
    model = AuthUser
    list_display = ('id', 'username')

    class Meta:
        app_label = 'myapp'


class AnotherAuthUserModelAdmin(ModelAdmin):
    model = AuthUser

    class Meta:
        app_label = 'myapp'
