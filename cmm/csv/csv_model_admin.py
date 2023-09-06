from django.contrib.admin import ModelAdmin
from cmm.csv import CsvBase
from cmm.models import get_field_names


class CsvModelAdmin(CsvBase):
    def __init__(self, model_admin: ModelAdmin) -> None:
        super().__init__()

        self._model_admin = model_admin

        model_fields = get_field_names(model_admin.model)
        self.model_fields = tuple(f for f in model_admin.list_display if f in model_fields)
        if not self.model_fields:
            self.model_fields = model_fields
        self.csv_headers = self.model_fields

    @property
    def model_admin(self) -> ModelAdmin:
        return self._model_admin

    @property
    def model_name(self) -> str:
        plural_name: str = self.model_admin.model._meta.verbose_name_plural
        return plural_name
