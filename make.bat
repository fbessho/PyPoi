@echo off

if "%1" == "" goto help

if "%1" == "help" (
    :help
	echo.Please use `make ^<target^>` where ^<target^> is one of
	echo.  exe              to make one file .exe
	echo.  exe-onefile      Same as `exe`
	echo.  exe-multi-file   to make distribution dir
    goto end
)


if "%1" == "exe-onefile" (
    goto exe
)


if "%1" == "exe" (
    :exe
    echo.Generate one file exe
    set PYPOI_BUILD_ONE_FILE=yes
    pyinstaller gui.spec
	goto end
)


if "%1" == "exe-multi-file" (
    echo.Generate distribution dir
    set PYPOI_BUILD_ONE_FILE=no
    pyinstaller gui.spec
	goto end
)


:end
