:: Variables:
:: Required: THRIFT_EXE


@ECHO OFF


:: Set up common properties
CALL "%CD%/Tools/batch/_common.bat"


:: Set and save the current directory
CD %ASSETS_PROJECT%/thrift
SET ROOT_DIR=%CD%


:: Move to the source folder
CD src


ECHO Generating thrift files with %THRIFT_EXE%.

:: Generate service files
FOR /f %%a IN ('dir /B *.thrift') DO ^
FOR %%b IN (java, py:utf8strings) DO ^
CALL "%THRIFT_EXE%" -o "%ROOT_DIR%" --gen %%b %%a

ECHO Service files have been generated.