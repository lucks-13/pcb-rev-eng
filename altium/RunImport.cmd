@echo off
set BOARD=%1
if "%BOARD%"=="" set BOARD=sample_board
set OUT_DIR=D:\Hack Club\pcb-rev-eng\outputs\%BOARD%
echo Output folder ready for Altium ImportDraftSchematic.pas: %OUT_DIR%
explorer "%OUT_DIR%"