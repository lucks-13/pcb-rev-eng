@echo off
set BOARD=%1
if "%BOARD%"=="" set BOARD=sample_board
set 
set OUT_DIR=%ROOT_DIR%\outputs\%BOARD%
echo Output folder ready for Altium ImportDraftSchematic.pas: %OUT_DIR%
explorer "%OUT_DIR%"