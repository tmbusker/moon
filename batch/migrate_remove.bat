echo off

REM Check for command-line arguments
if "%~1"=="" (
    call :Usage
    exit /b 1
)

setlocal enabledelayedexpansion

call %~dp0prepare.bat
pushd %project_path%
echo %cd%

for %%A in (%*) do (
    @REM  unapply all migrations for an app, resetting the app's schema to its initial state.
    echo python %project_path%\manage.py migrate %%A zero
    python %project_path%\manage.py migrate %%A zero

    if not exist "%%A\" goto :next_loop
    cd %%A
    echo rmdir /s /q %%A\migrations
    if exist "migrations\" rmdir /s /q migrations
    cd ..
    
    :next_loop
    rem next loop
)

REM Parameters should not contain admin sessions
python %project_path%\manage.py migrate admin zero
python %project_path%\manage.py migrate sessions zero

popd
endlocal
exit /b %errorlevel%

REM Function to display usage information
:Usage
echo Usage: %~n0 admin sessions cmm ...
echo.
exit /b 1
