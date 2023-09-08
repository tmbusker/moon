echo off
call prepare.bat

set DJANGO_SUPERUSER_PASSWORD=p09ol@Busking
set DJANGO_SUPERUSER_EMAIL=django.site.administrator@gmail.com

echo python %project_path%\manage.py createsuperuser --no-input --username admin
python %project_path%\manage.py createsuperuser --no-input --username admin

@REM echo python %project_path%\manage.py createsuperuser --no-input --username admin --database=test
@REM python %project_path%\manage.py createsuperuser --no-input --username admin --database=test
