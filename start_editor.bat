@echo off
chcp 65001 >nul
cd /d "%~dp0"
python app.py --game-dir "D:\JumpGame\300Hero"
if errorlevel 1 pause
