import math
from typing import Any, Dict, Tuple, Type
import io
import csv
from datetime import date, datetime
from django.db import transaction
from django.forms import ModelForm, modelform_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError
from cmm.models import SimpleTable
from cmm.csv import CsvBase, CsvLog, UploadMixin
from cmm.forms import get_modelform_error_messages, get_modelform_non_unique_error_codes


class CsvUploadMixin(CsvBase, UploadMixin):
    """
    CSVファイルの読込とModelFormを利用した有効性チェックを実装
    """

    header_row_number = 1
    # エラー件数がエラー容認度(%)を超えた場合は処理を中断する、エラーカウントはChunkごとに行う。
    error_tolerance_rate = 10
    # DBにすでに存在するレコードを上書きするかスキップするかを指定する。true: 上書き; false: スキップ
    is_overwrite_existing = True

    # CSVファイルからインポートされない項目のデフォルト値を設定する
    def get_default_values(self) -> Dict[str, Any]:
        default_values = {}
        return default_values

    def csv2model(self, csv_data: Dict[str, str]) -> Dict[str, Any]:
        """デフォルトでは同名項目を転送、CSVの項目名とDBのカラム名が同じではない場合はここでのマッピングが必要"""
        model_dict = {}
        for (k, v) in csv_data.items():
            if k in self.get_model_fields():
                if self.get_model_fields().get(k) == 'DateField':
                    model_dict[k] = datetime.strptime(v, self.date_format).date()
                elif self.get_model_fields().get(k) == 'DateTimeField':
                    model_dict[k] = datetime.strptime(v, self.datetime_format)
                else:
                    model_dict[k] = v
        # model_dict = {k: v for (k, v) in csv_data.items() if k in [f.name for f in self.get_model_fields()]}
        if issubclass(self.model, SimpleTable):
            updater = 'updater'
            if updater not in model_dict:
                model_dict[updater] = self.user_name

        return model_dict

    def __get_modelform_class(self) -> Type[ModelForm]:
        """Dynamically generate ModelForm class"""
        def disable_formfield(db_field, **kwargs):
            form_field = db_field.formfield(**kwargs)
            if form_field:
                form_field.widget.attrs['disabled'] = 'true'
            return form_field

        model_form: Type[ModelForm] = modelform_factory(self.model, fields=self.get_model_fields().keys(),
                                                        formfield_callback=disable_formfield)
        return model_form

    def __validate_by_modelform(self, csv_log: CsvLog):
        """ModelFormの入力チェックを実施"""
        modelform = self.__get_modelform_class()(self.csv2model(csv_log.row_content))

        if modelform.is_valid():
            csv_log.log_level = CsvLog.INFO
            csv_log.message = _('Newly imported row.')
            modelform.cleaned_data = modelform.data
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
                    self.model.objects.update_or_create(**csv_log.modelform.cleaned_data)
                else:
                    self.model.objects.create(**csv_log.modelform.cleaned_data)
                saved_rows += 1
            except IntegrityError as e:
                csv_log.log_level = CsvLog.ERROR
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

    def read_csv_file(self) -> int:
        """
        CSVファイルの読み込み処理、性能を考慮してchunkごとに読み込んでDBに保存する
        """

        # アップロード事前処理
        self.pre_import_processing()

        text_wrapper = io.TextIOWrapper(self.csv_file, encoding=self.encoding)
        csv_reader = csv.reader(text_wrapper, dialect=self.dialect)

        row_no = 0
        chunk: list[CsvLog] = []              # list[CsvLog]
        error_cnt = 0
        for row in csv_reader:
            row_no += 1

            # ヘッダー行と空行は読み飛ばすだけ、ログ記録は残さない
            if row_no <= self.header_row_number or not row:
                continue

            csv_log = CsvLog(file_name=self.csv_file.name,
                             row_no=row_no,
                             row_content=dict(zip(self.get_csv_field_names(), row)),
                             creator=self.user_name,
                             created_at=timezone.now(),
                             updater=self.user_name,
                             updated_at=timezone.now(),
                             version=1,
                             lot_number=self.lot_number)

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
        return row_no
