from typing import List
from django.db import models
from cmm.models import SimpleTable, VersionedTable, FlagChoices
from django.utils.translation import gettext_lazy as _


class BaseTable(SimpleTable, VersionedTable):
    class Meta:
        abstract = True


class Shikuchoson(BaseTable):
    """
    - 市区町村コード
        - 第１桁及び第２桁の番号： 01 から 47 までの連番号とする。
        - 第３桁、第４桁及び第５桁の番号
            - 都道府県: 000
            - 指定都市： 100（２以上の指定都市がある場合は、100から199 までのうちから定める。）
            - 指定都市の区:  101 から 199 までの連番号で表示する
            - 市（指定都市を除く）： 201 から 299 までの連番号で表示する
            - 町村: 301 から 799 までの連番号で表示する
    """
    shikuchoson_code = models.CharField(_('shikuchoson_code'), max_length=5, blank=False, null=False, unique=True)
    todofuken_name = models.CharField(_('todofuken_name'), max_length=8, blank=False, null=False)
    shikuchoson_name = models.CharField(_('shikuchoson_name'), max_length=24, blank=False, null=False)
    todofuken_kana = models.CharField(_('todofuken_kana'), max_length=8, blank=False, null=False)
    shikuchoson_kana = models.CharField(_('shikuchoson_kana'), max_length=24, blank=False, null=False)

    class Meta:
        # db_table = 'shikuchoson'
        verbose_name = _('shikuchoson')
        verbose_name_plural = _('shikuchoson')
        default_permissions: List[str] = []

        unique_together = ['shikuchoson_code']
        ordering = ['shikuchoson_code']


class ChangeTypeChoices(models.IntegerChoices):
    NO_CHANGE = 0, '変更なし'
    CHANGED = 1, '変更あり'
    ABOLITION = 2, '廃止'


class Postcode(BaseTable):
    """
    この郵便番号データファイルでは、以下の順に配列しています。
        1.全国地方公共団体コード（JIS X0401、X0402）……… 半角数字
        2.（旧）郵便番号（5桁）……………………………………… 半角数字
        3.郵便番号（7桁）……………………………………… 半角数字
        4.都道府県名 ………… 半角カタカナ（コード順に掲載） （注1）
        5.市区町村名 ………… 半角カタカナ（コード順に掲載） （注1）
        6.町域名 ……………… 半角カタカナ（五十音順に掲載） （注1）
        7.都道府県名 ………… 漢字（コード順に掲載） （注1,2）
        8.市区町村名 ………… 漢字（コード順に掲載） （注1,2）
        9.町域名 ……………… 漢字（五十音順に掲載） （注1,2）
        10.一町域が二以上の郵便番号で表される場合の表示 （注3） （「1」は該当、「0」は該当せず）
        11.小字毎に番地が起番されている町域の表示 （注4） （「1」は該当、「0」は該当せず）
        12.丁目を有する町域の場合の表示 （「1」は該当、「0」は該当せず）
        13.一つの郵便番号で二以上の町域を表す場合の表示 （注5） （「1」は該当、「0」は該当せず）
        14.更新の表示（注6）（「0」は変更なし、「1」は変更あり、「2」廃止（廃止データのみ使用））
        15.変更理由 （「0」は変更なし、「1」市政・区政・町政・分区・政令指定都市施行、「2」住居表示の実施、「3」区画整理、「4」郵便区調整等、「5」訂正、「6」廃止（廃止データのみ使用））
    """
    shikuchoson_code = models.CharField(_('shikuchoson_code'), max_length=5, blank=False, null=False)
    old_postcode = models.CharField(_('old_postcode'), max_length=5, blank=True, null=True)
    postcode = models.CharField(_('postcode'), max_length=7, blank=True, null=True)
    todofuken_kana = models.CharField(_('todofuken_kana'), max_length=8, blank=False, null=False)
    shikuchoson_kana = models.CharField(_('shikuchoson_kana'), max_length=24, blank=False, null=False)
    choiki_kana = models.CharField(_('choiki_kana'), max_length=500, blank=False, null=False)
    todofuken_name = models.CharField(_('todofuken_name'), max_length=8, blank=False, null=False)
    shikuchoson_name = models.CharField(_('shikuchoson_name'), max_length=24, blank=False, null=False)
    choiki_name = models.CharField(_('choiki_name'), max_length=500, blank=False, null=False)
    multiple_postcode_flag = models.IntegerField(_('multiple_postcode_flag'), blank=True, null=True,
                                                 choices=FlagChoices.choices, default=FlagChoices.OFF)
    banchi_overlap_flag = models.IntegerField(_('banchi_overlap_flag'), blank=True, null=True,
                                              choices=FlagChoices.choices, default=FlagChoices.OFF)
    has_chome_flag = models.IntegerField(_('has_chome_flag'), blank=True, null=True,
                                         choices=FlagChoices.choices, default=FlagChoices.OFF)
    multiple_choiki_flag = models.IntegerField(_('multiple_choiki_flag'), blank=True, null=True,
                                               choices=FlagChoices.choices, default=FlagChoices.OFF)
    change_type = models.IntegerField(_('change_type'), blank=True, null=True,
                                      choices=ChangeTypeChoices.choices, default=FlagChoices.OFF)
    change_reason = models.IntegerField(_('change_reason'), blank=True, null=True, default=0)

    class Meta:
        # db_table = 'postcode'
        verbose_name = _('postcode')
        verbose_name_plural = _('postcodes')
        default_permissions: List[str] = []

        unique_together = ['shikuchoson_code', 'postcode', 'choiki_name']
        ordering = ['postcode', 'choiki_kana']
