echo off
call prepare.bat

pushd %project_path%
python %project_path%\manage.py compilemessages -f %*
popd
