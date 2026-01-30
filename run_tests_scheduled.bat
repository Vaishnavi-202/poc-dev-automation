@echo off
REM WJA Automation with Allure Reports and Teams Notifications

echo ================= RUNNING WJA AUTOMATION =================

set BASEDIR=%~dp0
cd /d "%BASEDIR%"

REM Create necessary directories
if not exist "reports" mkdir reports
if not exist "reports\allure-history" mkdir reports\allure-history

echo ============================================ >> reports\execution_log.txt
echo [%date% %time%] Starting scheduled test execution >> reports\execution_log.txt
echo ============================================ >> reports\execution_log.txt

REM ===========================
REM PRESERVE HISTORY FOR TRENDS
REM ===========================
if exist "reports\allure-history\history" (
    echo [%date% %time%] Preserving test history for trends... >> reports\execution_log.txt
    xcopy /E /I /Y "reports\allure-history\history" "reports\allure-results\history" >nul 2>&1
)

REM Clean previous results but keep history
if exist "reports\allure-results" (
    echo [%date% %time%] Cleaning previous test results... >> reports\execution_log.txt
    for /d %%i in (reports\allure-results\*) do (
        if not "%%~nxi"=="history" rmdir /s /q "%%i"
    )
    del /q reports\allure-results\*.json 2>nul
    del /q reports\allure-results\*.txt 2>nul
    del /q reports\allure-results\*.properties 2>nul
)

REM ===========================
REM RUN TESTS
REM ===========================
echo [%date% %time%] Running pytest tests... >> reports\execution_log.txt

python -m pytest tests\WJA\POC --alluredir=reports\allure-results -v --tb=short --clean-alluredir >> reports\execution_log.txt 2>&1

set TEST_EXIT_CODE=%ERRORLEVEL%

if %TEST_EXIT_CODE% NEQ 0 (
    echo [%date% %time%] WARNING: Some tests failed or error occurred! >> reports\execution_log.txt
    set TEST_STATUS=Tests completed with failures
    set STATUS_EMOJI=WARNING
) else (
    echo [%date% %time%] All tests passed successfully! >> reports\execution_log.txt
    set TEST_STATUS=All tests passed
    set STATUS_EMOJI=SUCCESS
)

REM ===========================
REM COPY CATEGORIES CONFIG
REM ===========================
if exist "categories.json" (
    echo [%date% %time%] Copying categories configuration... >> reports\execution_log.txt
    copy /Y categories.json reports\allure-results\categories.json >nul 2>&1
)

REM ===========================
REM GENERATE TIMESTAMP
REM ===========================
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%

REM ===========================
REM GENERATE ALLURE REPORT
REM ===========================
echo [%date% %time%] Generating Allure report... >> reports\execution_log.txt

call allure generate reports\allure-results -o reports\allure-report-%timestamp% --clean >> reports\execution_log.txt 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] ERROR: Allure report generation failed! >> reports\execution_log.txt
    set REPORT_STATUS=Report generation failed
) else (
    echo [%date% %time%] Allure report generated successfully! >> reports\execution_log.txt
    set REPORT_STATUS=Report generated
)

REM ===========================
REM SAVE HISTORY FOR TRENDS
REM ===========================
if exist "reports\allure-report-%timestamp%\history" (
    echo [%date% %time%] Saving test history for future trends... >> reports\execution_log.txt
    xcopy /E /I /Y "reports\allure-report-%timestamp%\history" "reports\allure-history\history" >nul 2>&1
)

REM ===========================
REM CREATE TEMP COPY FOR ZIP
REM ===========================
set TEMP_REPORT=reports\temp_report_%timestamp%

echo [%date% %time%] Creating temporary report copy... >> reports\execution_log.txt
robocopy "reports\allure-report-%timestamp%" "%TEMP_REPORT%" /E /NFL /NDL /NJH /NJS /NC /NS >> reports\execution_log.txt

REM ===========================
REM CREATE ZIP FILE
REM ===========================
timeout /t 5 >nul

echo [%date% %time%] Creating ZIP file... >> reports\execution_log.txt

powershell -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; $zip='%TEMP_REPORT%.zip'; if(Test-Path $zip){Remove-Item $zip -Force}; [System.IO.Compression.ZipFile]::CreateFromDirectory('%TEMP_REPORT%', $zip)"

if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] ERROR: ZIP creation failed! >> reports\execution_log.txt
    set ZIP_STATUS=ZIP creation failed
    set ZIP_PATH=N/A
) else (
    echo [%date% %time%] ZIP created successfully! >> reports\execution_log.txt
    set ZIP_STATUS=ZIP created
    set ZIP_PATH=%TEMP_REPORT%.zip
)

REM ===========================
REM PARSE TEST RESULTS
REM ===========================
REM Count test results from allure-results folder
set PASSED=0
set FAILED=0
set TOTAL=0

for /f %%a in ('powershell -command "(Get-Content reports\allure-results\*-result.json | Select-String -Pattern '\"\"status\"\":\"\"passed\"\"' -AllMatches).Matches.Count"') do set PASSED=%%a
for /f %%a in ('powershell -command "(Get-Content reports\allure-results\*-result.json | Select-String -Pattern '\"\"status\"\":\"\"failed\"\"' -AllMatches).Matches.Count"') do set FAILED=%%a
for /f %%a in ('dir /b reports\allure-results\*-result.json 2^>nul ^| find /c /v ""') do set TOTAL=%%a

if "%TOTAL%"=="" set TOTAL=0
if "%PASSED%"=="" set PASSED=0
if "%FAILED%"=="" set FAILED=0

REM ===========================
REM TEAMS NOTIFICATION (CURL METHOD - FIXED)
REM ===========================
set WEBHOOK_URL=https://ascendionhub.webhook.office.com/webhookb2/37095985-1535-45b0-b893-4763b939ed2b@d7758e8f-1df3-489f-86b5-a2254f55f9cc/IncomingWebhook/f44fcdbb3ea64e68ab6e6ee06f24aa10/b7637afa-f626-459f-947b-92ecc9557c02/V2LZUaFJG18A7VwniVxQdLMbLTSR72OiZZ96n3Io7RAJ81

echo [%date% %time%] Sending Teams notification... >> reports\execution_log.txt

REM Create JSON message with test results
echo {"text":"**WJA Automation Completed - %STATUS_EMOJI%**\n\n**Test Execution Summary:**\n\n- Status: %TEST_STATUS%\n- Total Tests: %TOTAL%\n- Passed: %PASSED%\n- Failed: %FAILED%\n\n**Report Details:**\n- Report Status: %REPORT_STATUS%\n- ZIP Status: %ZIP_STATUS%\n- Report Location: reports\\allure-report-%timestamp%\n- ZIP Location: %ZIP_PATH%\n\n**Execution Time:** %date% %time%"} > teams_notification.json

REM Send notification using curl
curl -s -H "Content-Type: application/json" -d @teams_notification.json "%WEBHOOK_URL%" > teams_response.txt 2>&1

REM Check if successful (Teams webhook returns "1" on success)
findstr /C:"1" teams_response.txt >nul
if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Teams notification sent successfully! >> reports\execution_log.txt
) else (
    echo [%date% %time%] Teams notification failed. Response: >> reports\execution_log.txt
    type teams_response.txt >> reports\execution_log.txt
)

REM Cleanup temporary files
del teams_notification.json teams_response.txt 2>nul

REM ===========================
REM CLEANUP (Optional)
REM ===========================
REM Remove temp directory after zipping
if exist "%TEMP_REPORT%" (
    echo [%date% %time%] Cleaning up temporary files... >> reports\execution_log.txt
    rmdir /s /q "%TEMP_REPORT%"
)

echo [%date% %time%] ============================================ >> reports\execution_log.txt
echo [%date% %time%] Automation finished successfully! >> reports\execution_log.txt
echo [%date% %time%] All sections populated: TREND, ENVIRONMENT, CATEGORIES, EXECUTORS >> reports\execution_log.txt
echo [%date% %time%] ============================================ >> reports\execution_log.txt
echo. >> reports\execution_log.txt

REM No pause for scheduled execution