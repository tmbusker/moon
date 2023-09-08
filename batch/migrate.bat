echo off

REM Check for command-line arguments
if "%~1"=="" (
    call :Usage
    exit /b 1
)

setlocal enabledelayedexpansion

call prepare
pushd %project_path%
echo %cd%

for %%A in (%*) do (
    @REM  unapply all migrations for an app, resetting the app's schema to its initial state.
    echo python %project_path%\manage.py makemigrations %%A
    python %project_path%\manage.py makemigrations %%A

    echo python %project_path%\manage.py migrate %%A
    python %project_path%\manage.py migrate %%A
)

REM Parameters should not contain admin sessions
python %project_path%\manage.py migrate admin
python %project_path%\manage.py migrate sessions

popd
endlocal
exit /b %errorlevel%

REM Function to display usage information
:Usage
echo Usage: %~n0 admin sessions cmm ...
echo.
exit /b 1
