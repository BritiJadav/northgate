@echo off
title Push Northgate to GitHub
cd /d "C:\Users\v69-labuser449619\Desktop\Northgate"
echo ===================================================
echo Pushing Northgate repository to github.com/BritiJadav/northgate
echo ===================================================
echo.
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ===================================================
    echo SUCCESS! Your code has been pushed to GitHub:
    echo https://github.com/BritiJadav/northgate
    echo ===================================================
) else (
    echo.
    echo If GitHub asks for authentication, sign in with your GitHub account.
    echo Note: If asked for password, use a Personal Access Token (PAT):
    echo https://github.com/settings/tokens
)
pause
