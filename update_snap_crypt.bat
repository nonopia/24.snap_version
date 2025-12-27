@echo off
title snap_crypt 업데이트
echo ========================================
echo snap_crypt 자동 업데이트
echo ========================================
echo.
echo 업데이트를 진행합니다...
echo 잠시만 기다려주세요.
echo.

REM 프로세스 종료 대기 (5초)
timeout /t 5 /nobreak > nul

REM 파일 교체
echo 파일 교체 중...
move /Y "C:\Users\nono\AppData\Local\Temp\tmpm2fs_q7s\snap_crypt_update.exe" "D:\55.Project\24.snap_version\up_auto_updater.py" > nul 2>&1

REM 교체 성공 여부 확인
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 업데이트 완료!
    echo ========================================
    echo.
    
    REM 백업 파일 삭제
    if exist "D:\55.Project\24.snap_version\up_auto_updater.exe.backup" (
        del "D:\55.Project\24.snap_version\up_auto_updater.exe.backup" > nul 2>&1
    )
    
    echo 프로그램을 다시 시작합니다...
    timeout /t 2 /nobreak > nul
    
    REM 프로그램 재시작
    start "" "D:\55.Project\24.snap_version\up_auto_updater.py"
) else (
    echo.
    echo ========================================
    echo 업데이트 실패!
    echo ========================================
    echo.
    echo 백업에서 복원 중...
    
    REM 백업에서 복원
    if exist "D:\55.Project\24.snap_version\up_auto_updater.exe.backup" (
        move /Y "D:\55.Project\24.snap_version\up_auto_updater.exe.backup" "D:\55.Project\24.snap_version\up_auto_updater.py" > nul 2>&1
        echo 복원 완료
    )
    
    echo 프로그램을 다시 시작합니다...
    timeout /t 2 /nobreak > nul
    
    REM 프로그램 재시작
    start "" "D:\55.Project\24.snap_version\up_auto_updater.py"
)

REM 임시 파일 정리
if exist "C:\Users\nono\AppData\Local\Temp\tmpm2fs_q7s" (
    rmdir /S /Q "C:\Users\nono\AppData\Local\Temp\tmpm2fs_q7s" > nul 2>&1
)

REM 배치 파일 자체 삭제
del "%~f0" > nul 2>&1
