@echo off

SET PATH=%PATH%;C:\WINDOWS;C:\WINDOWS\SYSTEM32;C:\PYTHON34;%ProgramFiles%\7-Zip

py -c "from partmgr.core.version import VERSION_STRING; print(VERSION_STRING)" > version.txt
set /p version= < version.txt
del version.txt

set distdir=partmgr-win-standalone-%version%
set sfxfile=partmgr-win-%version%.package.exe
set bindir=%distdir%\partmgr-bin

rd /S /Q build 2>NUL
rd /S /Q %distdir% 2>NUL
del %sfxfile% 2>NUL

echo Building standalone Windows executable for partmgr v%version%...
echo.

echo Please select GUI framework:
REM echo   1)  Build with PyQt5 (default)
echo   1)  Build with PySide4 (default)
set /p framework=Selection: 
if "%framework%" == "" goto framework_pyside4
REM if "%framework%" == "1" goto framework_pyqt5
if "%framework%" == "1" goto framework_pyside4
echo "Error: Invalid selection"
pause
exit

:framework_pyqt5
echo Using PyQt5
set excludes=PySide
goto select_freezer

:framework_pyside4
echo Using PySide4
set excludes=PyQt5
goto select_freezer


:select_freezer
echo.
echo Please select freezer:
echo   1)  Build 'cx_Freeze' based distribution (default)
echo   2)  Build 'py2exe' based distribution
set /p buildtype=Selection: 
if "%buildtype%" == "" goto build_cxfreeze
if "%buildtype%" == "1" goto build_cxfreeze
if "%buildtype%" == "2" goto build_py2exe
echo "Error: Invalid selection"
pause
exit


:build_cxfreeze
set buildtype=1
echo === Creating the cx_Freeze distribution
timeout /T 2 /NOBREAK >NUL
mkdir %distdir%
if ERRORLEVEL 1 goto error_prep
mkdir %bindir%
if ERRORLEVEL 1 goto error_prep
py setup.py build_exe ^
	--build-exe=%bindir% ^
	--optimize=2 ^
	--excludes=%excludes% ^
	--silent
if ERRORLEVEL 1 goto error_exe
goto copy_files


:build_py2exe
set buildtype=2
echo === Creating the py2exe distribution
timeout /T 2 /NOBREAK >NUL
mkdir %distdir%
if ERRORLEVEL 1 goto error_prep
mkdir %bindir%
if ERRORLEVEL 1 goto error_prep
py setup.py py2exe ^
	--dist-dir=%bindir% ^
	--optimize=2 ^
	--bundle-files=3 ^
	--ignores=win32api,win32con,readline ^
	--excludes=%excludes% ^
	--quiet
if ERRORLEVEL 1 goto error_exe
goto copy_files


:copy_files
echo === Copying additional files
copy example.pmg %distdir%\
if ERRORLEVEL 1 goto error_copy
copy COPYING %distdir%\LICENSE.txt
if ERRORLEVEL 1 goto error_copy


echo === Generating startup wrapper
set wrapper=%distdir%\partmgr.bat
echo @echo off> %wrapper%
if ERRORLEVEL 1 goto error_wrapper
echo start /Dpartmgr-bin partmgr-gui.exe %%1>> %wrapper%
if ERRORLEVEL 1 goto error_wrapper


echo === Creating the distribution archive
7z a -mx=9 -sfx7z.sfx %sfxfile% %distdir%
if ERRORLEVEL 1 goto error_7z


echo ---
echo finished
pause
exit




:error_prep
echo FAILED to prepare environment
goto error

:error_exe
echo FAILED to build exe
goto error

:error_copy
echo FAILED to copy files
goto error

:error_wrapper
echo FAILED to create wrapper
goto error

:error_7z
echo FAILED to create archive
goto error

:error
pause
exit
