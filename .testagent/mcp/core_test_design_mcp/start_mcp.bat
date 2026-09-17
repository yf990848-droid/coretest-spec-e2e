@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM MCP Bootstrap Launcher
REM core_test_design_mcp
REM ==========================================


REM 当前脚本目录

set MCP_DIR=%~dp0


REM 获取扩展根目录

for %%I in ("%MCP_DIR%..\..\..") do set ROOT_DIR=%%~fI


echo [MCP] Root: %ROOT_DIR%


REM ==========================================
REM 1. 已存在虚拟环境，直接启动
REM ==========================================

if exist "%ROOT_DIR%\.venv\Scripts\python.exe" (

    echo [MCP] Using existing venv

    "%ROOT_DIR%\.venv\Scripts\python.exe" -c "import requests, fastmcp, cryptography" >nul 2>nul
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

    "%ROOT_DIR%\.venv\Scripts\python.exe" ^
    "%MCP_DIR%mcp_server.py"

    exit /b !errorlevel!
)


REM ==========================================
REM 2. 查找 Python 3.10+
REM ==========================================

set PYTHON_EXE=


REM ------------------------------------------
REM 2.1 Python Launcher
REM ------------------------------------------

where py >nul 2>nul

if %errorlevel%==0 (

    py -3.10 --version >nul 2>nul

    if !errorlevel!==0 (
        set PYTHON_EXE=py -3.10
    )
)


REM ------------------------------------------
REM 2.2 当前 PATH Python
REM ------------------------------------------

if "!PYTHON_EXE!"=="" (

    python --version >nul 2>nul

    if !errorlevel!==0 (

        python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)"

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
        -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)"

        if !errorlevel!==0 (
            set PYTHON_EXE="%USERPROFILE%\AppData\Local\miniforge3\python.exe"
        )
    )
)


REM ==========================================
REM 3. 未找到 Python 3.10+
REM ==========================================

if "!PYTHON_EXE!"=="" (

    echo [MCP ERROR] Need Python 3.10+

    exit /b 1
)


echo [MCP] Using Python:

!PYTHON_EXE! --version


REM ==========================================
REM 4. 创建虚拟环境
REM ==========================================

echo [MCP] Creating venv


!PYTHON_EXE! -m venv "%ROOT_DIR%\.venv"


if %errorlevel% neq 0 (

    echo [MCP ERROR] Create venv failed

    exit /b 1
)


REM ==========================================
REM 5. 升级 pip
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
REM 6. 安装依赖
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
REM 7. 启动 MCP Server
REM ==========================================

echo [MCP] Starting server


"%ROOT_DIR%\.venv\Scripts\python.exe" ^
"%MCP_DIR%mcp_server.py"


exit /b %errorlevel%
