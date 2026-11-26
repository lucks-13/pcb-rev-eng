@echo off
set BOARD=%1
if "%BOARD%"=="" set BOARD=complex_board
set ROOT_DIR=%~dp0..
set OUT_DIR=%ROOT_DIR%\outputs\%BOARD%
echo Output folder ready : %OUT_DIR%
explorer "%OUT_DIR%"