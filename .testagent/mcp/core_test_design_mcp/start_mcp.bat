@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM MCP Bootstrap Launcher
REM core_test_design_mcp
REM ==========================================


REM Script directory

set MCP_DIR=%~dp0


REM Extension root directory

for %%I in ("%MCP_DIR%..\..\..") do set ROOT_DIR=%%~fI


echo [MCP] Root: %ROOT_DIR%


REM ==========================================
REM 1. Validate and reuse the existing virtual environment
REM ==========================================

if exist "%ROOT_DIR%\.venv\Scripts\python.exe" (

    echo [MCP] Using existing venv

    "%ROOT_DIR%\.venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"
    if !errorlevel! neq 0 (
        echo [MCP ERROR] Existing venv requires Python 3.11+. Python 3.12 is recommended.
        echo [MCP ERROR] Rename "%ROOT_DIR%\.venv" as a backup, then run this script again.
        exit /b 1
    )

    "%ROOT_DIR%\.venv\Scripts\python.exe" -c "import requests, cryptography; from fastmcp import FastMCP" >nul 2>nul
    if !errorlevel! neq 0 (
        echo [MCP] Installing missing dependencies
        "%ROOT_DIR%\.venv\Scripts\python.exe" ^
        -m pip install ^
        -r "%ROOT_DIR%\requirements.txt" ^
        -i http://cmc-cd-mirror.rnd.huawei.com/pypi/simple/ ^
        --trusted-host cmc-cd-mirror.rnd.huawei.com
        if !errorlevel! neq 0 (
            echo [MCP ERROR] Install dependencies failed
            exit /b 1
        )
    )

    "%ROOT_DIR%\.venv\Scripts\python.exe" -c "import requests, cryptography; from fastmcp import FastMCP"
    if !errorlevel! neq 0 (
        echo [MCP ERROR] Dependency import check failed
        exit /b 1
    )

    "%ROOT_DIR%\.venv\Scripts\python.exe" ^
    "%MCP_DIR%mcp_server.py"

    exit /b !errorlevel!
)


REM ==========================================
REM 2. Find Python 3.11+
REM ==========================================

set PYTHON_EXE=


REM ------------------------------------------
REM 2.1 Python Launcher
REM ------------------------------------------

where py >nul 2>nul

if %errorlevel%==0 (

    REM Prefer the verified Python 3.12 runtime, then try the default Python 3.
    py -3.12 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul

    if !errorlevel!==0 (
        set PYTHON_EXE=py -3.12
    )

    if "!PYTHON_EXE!"=="" (
        py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
        if !errorlevel!==0 (
            set PYTHON_EXE=py -3
        )
    )
    if "!PYTHON_EXE!"=="" (
        py -3.11 -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
        if !errorlevel!==0 (
            set PYTHON_EXE=py -3.11
        )
    )
)


REM ------------------------------------------
REM 2.2 Python on PATH
REM ------------------------------------------

if "!PYTHON_EXE!"=="" (

    python --version >nul 2>nul

    if !errorlevel!==0 (

        python -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)"

        if !errorlevel!==0 (
            set PYTHON_EXE=python
        )
    )
)


REM ------------------------------------------
REM 2.3 Miniforge Python
REM ------------------------------------------

if "!PYTHON_EXE!"=="" (

    if exist "%USERPROFILE%\AppData\Local\miniforge3\python.exe" (

        "%USERPROFILE%\AppData\Local\miniforge3\python.exe" ^
        -c "import sys; exit(0 if sys.version_info >= (3,11) else 1)"

        if !errorlevel!==0 (
            set PYTHON_EXE="%USERPROFILE%\AppData\Local\miniforge3\python.exe"
        )
    )
)


REM ==========================================
REM 3. No supported Python found
REM ==========================================

if "!PYTHON_EXE!"=="" (

    echo [MCP ERROR] Need Python 3.11+

    exit /b 1
)


echo [MCP] Using Python:

!PYTHON_EXE! --version


REM ==========================================
REM 4. Create virtual environment
REM ==========================================

echo [MCP] Creating venv


!PYTHON_EXE! -m venv "%ROOT_DIR%\.venv"


if %errorlevel% neq 0 (

    echo [MCP ERROR] Create venv failed

    exit /b 1
)


REM ==========================================
REM 5. Upgrade pip
REM ==========================================

echo [MCP] Upgrade pip


"%ROOT_DIR%\.venv\Scripts\python.exe" ^
-m pip install --upgrade pip ^
-i http://cmc-cd-mirror.rnd.huawei.com/pypi/simple/ ^
--trusted-host cmc-cd-mirror.rnd.huawei.com


if %errorlevel% neq 0 (

    echo [MCP ERROR] Upgrade pip failed

    exit /b 1
)


REM ==========================================
REM 6. Install dependencies
REM ==========================================

echo [MCP] Installing dependencies


"%ROOT_DIR%\.venv\Scripts\python.exe" ^
-m pip install ^
-r "%ROOT_DIR%\requirements.txt" ^
-i http://cmc-cd-mirror.rnd.huawei.com/pypi/simple/ ^
--trusted-host cmc-cd-mirror.rnd.huawei.com


if %errorlevel% neq 0 (

    echo [MCP ERROR] Install dependencies failed

    exit /b 1
)


REM ==========================================
REM 7. Start MCP server
REM ==========================================

"%ROOT_DIR%\.venv\Scripts\python.exe" -c "import requests, cryptography; from fastmcp import FastMCP"
if %errorlevel% neq 0 (
    echo [MCP ERROR] Dependency import check failed
    exit /b 1
)

echo [MCP] Starting server


"%ROOT_DIR%\.venv\Scripts\python.exe" ^
"%MCP_DIR%mcp_server.py"


exit /b %errorlevel%
