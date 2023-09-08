echo off
call prepare.bat

pushd %project_path%
@REM python %project_path%\manage.py makemessages -all
python %project_path%\manage.py makemessages -l ja
popd
