import math
from typing import Any, Dict, List, Tuple, Type
import io
import csv
from django.db import transaction
from django.forms import ModelForm, modelform_factory
from django.contrib.admin import ModelAdmin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError
from cmm.csv import CsvModelAdmin, CsvLog
from cmm.forms import get_modelform_error_messages, get_modelform_non_unique_error_codes
from cmm.models import get_unique_constraint_name, get_unique_constrains


class CsvUploader(CsvModelAdmin):
    """
    CSVファイルの読込とModelFormを利用した有効性チェックを実装
    """

    def __init__(self, model_admin: ModelAdmin) -> None:
        super().__init__(model_admin)

        self._header_row_number = 1
        self._error_tolerance_rate = 10

        # CSVファイルからインポートされない項目のデフォルト値を設定する
        self.default_values: Dict[str, Any] = {}
        # DBにすでに存在するレコードを上書きするかスキップするかを指定する。true: 上書き; false: スキップ
        self.is_overwrite_existing = True
        self.unique_constraints = get_unique_constrains(model_admin.model)

    @property
    def header_row_number(self) -> int:
        """ ヘッダーの行数 """
        return self._header_row_number

    @header_row_number.setter
    def header_row_number(self, value: int):
        if value >= 0:
            self._header_row_number = value
        else:
            raise ValueError()

    @property
    def error_tolerance_rate(self) -> int:
        """
        エラー容認度(%)
        エラー件数がエラー容認度を超えた場合は処理を中断する、エラーカウントはChunkごとに行う。
        """
        return self._error_tolerance_rate

    @error_tolerance_rate.setter
    def error_tolerance_rate(self, value: int):
        if value >= 0 and value <= 100:
            self._error_tolerance_rate = value
        else:
            raise ValueError()

    def csv2model(self, csv_data: Dict[str, str]) -> Dict[str, Any]:
        """デフォルトでは同名項目を転送、必要に応じてOverride"""
        return self.default_values | {k: v for (k, v) in csv_data.items() if k in self.model_fields}

    def __get_modelform_class(self) -> Type[ModelForm]:
        """Dynamically generate ModelForm class"""
        def disable_formfield(db_field, **kwargs):
            form_field = db_field.formfield(**kwargs)
            if form_field:
                form_field.widget.attrs['disabled'] = 'true'
            return form_field

        non_relational_fields = (f.name for f in self.model_admin.model._meta.concrete_fields)
        non_relational_model_fields = tuple(f for f in self.model_fields if f in (non_relational_fields))
        non_relational_default_fields = tuple(k for k in self.default_values if k in (non_relational_fields))
        form_fields = tuple(set(non_relational_model_fields + non_relational_default_fields))
        model_form: Type[ModelForm] = modelform_factory(self.model_admin.model, fields=form_fields,
                                                        formfield_callback=disable_formfield)
        return model_form

    def __validate_by_modelform(self, csv_log: CsvLog):
        """ModelFormの入力チェックを実施"""
        modelform = self.__get_modelform_class()(self.csv2model(csv_log.row_content))

        if modelform.is_valid():
            csv_log.log_level = CsvLog.INFO
            csv_log.message = _('Newly imported row.')
            csv_log.modelform = modelform
        else:
            non_unique_error_codes = get_modelform_non_unique_error_codes(modelform)
            if not non_unique_error_codes:      # only unique violation
                if self.is_overwrite_existing:
                    csv_log.message = _("Update existing row.")
                    csv_log.log_level = CsvLog.INFO
                    csv_log.edit_type = CsvLog.UPDATE
                    modelform.cleaned_data = modelform.data
                    csv_log.modelform = modelform
                else:
                    csv_log.log_level = CsvLog.WARN     # DBと重複したのでスキップする
                    csv_log.message = get_modelform_error_messages(modelform)
            else:
                csv_log.log_level = CsvLog.ERROR
                csv_log.message = get_modelform_error_messages(modelform)

    def __has_too_many_errors(self, error_cnt: int) -> bool:
        error_limit = math.floor(self.chunk_size * self.error_tolerance_rate / 100)
        return error_cnt > error_limit

    def __save(self, chunk: list[CsvLog]) -> int:
        """save valid data and log info to database"""
        saved_rows: int = self.__save2db(chunk)
        self.__save2db_csv_logs(chunk)
        return saved_rows

    @transaction.atomic
    def __save2db(self, chunk: list[CsvLog]) -> int:
        """DB保存処理"""
        saved_rows = 0
        valid_data = [v for v in chunk if v.log_level == CsvLog.INFO]

        for csv_log in valid_data:
            try:
                if self.is_overwrite_existing:
                    self.model_admin.model.objects.update_or_create(**csv_log.modelform.cleaned_data)
                else:
                    self.model_admin.model.objects.create(**csv_log.modelform.cleaned_data)
                saved_rows += 1
            except IntegrityError as e:
                csv_log.message = e.args[0]

        return saved_rows

    @transaction.atomic
    def __save2db_csv_logs(self, chunk: list[CsvLog]) -> None:
        """インポートログ情報をDBに記録する"""
        CsvLog.objects.bulk_create([csv_log.convert_content2json() for csv_log in chunk])

    def pre_import_processing(self, *args, **kwargs):
        """CSV importの前処理"""

    def post_import_processing(self, *args, **kwargs):
        """CSV importの後処理"""

    def read_csv_file(self, csv_file, login_user_name: str) -> Tuple[int, str]:
        """
        CSVファイルの読み込み処理
        性能を考慮してchunkごとに読み込んでDBに保存する
        """

        lot_number = str(hash(csv_file.name + login_user_name + str(timezone.now())))
        # アップロード事前処理
        self.pre_import_processing()

        text_wrapper = io.TextIOWrapper(csv_file, encoding=self.encoding)
        csv_reader = csv.reader(text_wrapper, dialect=self.dialect)

        row_no = 0
        chunk: list[CsvLog] = []              # list[CsvLog]
        error_cnt = 0
        for row in csv_reader:
            row_no += 1

            # ヘッダー行と空行は読み飛ばすだけ、ログ記録は残さない
            if row_no <= self.header_row_number or not row:
                continue

            csv_log = CsvLog(file_name=csv_file.name,
                             row_no=row_no,
                             row_content=dict(zip(self.csv_headers, row)),
                             creator=login_user_name,
                             lot_number=lot_number)

            self.__validate_by_modelform(csv_log)
            chunk.append(csv_log)

            if len(chunk) >= self.chunk_size:
                saved_rows = self.__save(chunk)

                error_cnt += len(chunk) - saved_rows
                if self.__has_too_many_errors(error_cnt):
                    break
                chunk.clear()
        else:
            if chunk:
                self.__save(chunk)

        # インポートファイルを読み込みがすべて完了した後の処理
        self.post_import_processing()
        return (row_no, lot_number)
