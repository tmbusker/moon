echo off
@REM setlocal EnableExtensions EnableDelayedExpansion

pushd %~dp0
echo %cd% | findstr /C:"scripts\\django" >nul
if %errorlevel%==0 (
    goto :outside_django_project
) else (
    goto :inside_django_project
)

:outside_django_project
echo Run at outside of a django project
if "%project_path%" NEQ "" goto :end
cd ..\..
set base_path=%cd%
set project_path=%base_path%\busking
set "path=%project_path%\bat;%path%"
set "venv_path=%base_path%\venv"
goto :end

:inside_django_project
echo Run at inside of a django project
cd ..

@REM check to avoid duplicate execution
if "%project_path%" EQU "%cd%" goto :set_base_path
set "project_path=%cd%"
set "path=%project_path%\bat;%path%"

:set_base_path
cd ..
if "%base_path%" EQU "%cd%" goto :end
set "base_path=%cd%"
set "venv_path=%base_path%\venv"

:end
echo Project Path: %project_path%
echo Python Virtual Environment: %venv_path%
popd
