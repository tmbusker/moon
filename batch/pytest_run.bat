echo off
for /F "tokens=1-3 delims=-/ " %%a in ('date /t') do set date_str=%%a%%b%%c
for /F "tokens=1-2 delims=: " %%a in ('time /t') do set time_str=%%a%%b

set "logfile=%~n0_%date_str%_%time_str%.log"

pushd %~dp0
cd ..
pytest cmm -v --cov=cmm --cov-report=html --cov-config=.coveragerc --reuse-db >%logfile% 2>&1

set exit_code=%errorlevel%
@REM Check the exit code
if %exit_code% equ 0 (
    echo All tests passed successfully.
) else (
    echo There were test failures or errors.
)

popd
exit /b %exit_code%
