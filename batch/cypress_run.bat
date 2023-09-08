echo off
for /F "tokens=1-3 delims=-/ " %%a in ('date /t') do set date_str=%%a%%b%%c
for /F "tokens=1-2 delims=: " %%a in ('time /t') do set time_str=%%a%%b

pushd %~dp0
cd ..

set "logfile=%~n0_%date_str%_%time_str%.log"

echo Create groups
call npx cypress run --spec cypress/e2e/create_groups.cy.js > %logfile% 2>&1
if %errorlevel% geq 1 goto :batch_end

echo Create users
call npx cypress run --spec cypress/e2e/create_users.cy.js >> %logfile% 2>&1
if %errorlevel% geq 1 goto :batch_end

echo Delete users
call npx cypress run --spec cypress/e2e/delete_users.cy.js >> %logfile% 2>&1
if %errorlevel% geq 1 goto :batch_end

echo Delete groups
call npx cypress run --spec cypress/e2e/delete_groups.cy.js >> %logfile% 2>&1

:batch_end
set exit_code=%errorlevel%
@REM Check the exit code(メッセージはなぜか表示されないが、エラーコードは正しく出力される)
if %exit_code% equ 0 (
    echo All tests passed successfully.
) else (
    echo There were test failures or errors.
)

popd
exit /b %exit_code%
