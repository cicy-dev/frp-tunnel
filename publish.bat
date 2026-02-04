@echo off
REM 一键发布到 PyPI 脚本 (Windows)
echo 🚀 一键发布 frp-tunnel 到 PyPI
echo ==============================

REM 检查是否在正确目录
if not exist "pyproject.toml" (
    echo ❌ 错误: 未找到 pyproject.toml，请在项目根目录运行
    exit /b 1
)

REM 检查是否在 GitHub Actions 环境
if defined GITHUB_ACTIONS (
    echo 🤖 检测到 GitHub Actions 环境
    if not defined PYPI_API_TOKEN (
        echo ❌ GitHub Actions 需要设置 PYPI_API_TOKEN secret
        exit /b 1
    )
    if not defined TEST_PYPI_API_TOKEN (
        echo ❌ GitHub Actions 需要设置 TEST_PYPI_API_TOKEN secret
        exit /b 1
    )
) else (
    echo 💻 本地环境 - 需要输入令牌
    
    REM 检查是否有 PyPI 令牌
    if not exist "%USERPROFILE%\.pypirc" (
        echo.
        echo 📝 需要设置 PyPI 令牌
        set /p TEST_PYPI_TOKEN="请输入你的 TestPyPI API 令牌 (以 pypi- 开头): "
        set /p PYPI_TOKEN="请输入你的 PyPI API 令牌 (以 pypi- 开头): "
        
        echo [distutils] > "%USERPROFILE%\.pypirc"
        echo index-servers = >> "%USERPROFILE%\.pypirc"
        echo     pypi >> "%USERPROFILE%\.pypirc"
        echo     testpypi >> "%USERPROFILE%\.pypirc"
        echo. >> "%USERPROFILE%\.pypirc"
        echo [pypi] >> "%USERPROFILE%\.pypirc"
        echo repository = https://upload.pypi.org/legacy/ >> "%USERPROFILE%\.pypirc"
        echo username = __token__ >> "%USERPROFILE%\.pypirc"
        echo password = %PYPI_TOKEN% >> "%USERPROFILE%\.pypirc"
        echo. >> "%USERPROFILE%\.pypirc"
        echo [testpypi] >> "%USERPROFILE%\.pypirc"
        echo repository = https://test.pypi.org/legacy/ >> "%USERPROFILE%\.pypirc"
        echo username = __token__ >> "%USERPROFILE%\.pypirc"
        echo password = %TEST_PYPI_TOKEN% >> "%USERPROFILE%\.pypirc"
        
        echo ✅ PyPI 令牌已保存
        
        REM 设置 GitHub secrets
        echo.
        echo 🔐 设置 GitHub secrets...
        where gh >nul 2>&1
        if %errorlevel% equ 0 (
            echo %PYPI_TOKEN% | gh secret set PYPI_API_TOKEN
            echo %TEST_PYPI_TOKEN% | gh secret set TEST_PYPI_API_TOKEN
            echo ✅ GitHub secrets 已设置
        ) else (
            echo ⚠️  未找到 gh CLI，请手动设置 GitHub secrets:
            echo    - PYPI_API_TOKEN
            echo    - TEST_PYPI_API_TOKEN
            echo    在: https://github.com/cicy-dev/frp-tunnel/settings/secrets/actions
        )
    ) else (
        echo ✅ 找到现有的 PyPI 配置
    )
)

REM 安装构建依赖
echo.
echo 📦 安装构建依赖...
pip install --upgrade build twine

REM 清理旧构建
echo.
echo 🧹 清理旧构建...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM 构建包
echo.
echo 📦 构建包...
python -m build

REM 显示构建的包
echo.
echo 📋 构建的包:
dir dist

REM 本地环境：先发布到 TestPyPI 测试
if not defined GITHUB_ACTIONS (
    echo.
    echo 🧪 本地环境 - 先发布到 TestPyPI 测试...
    twine upload --repository testpypi dist/*
    
    if %errorlevel% equ 0 (
        echo ✅ TestPyPI 发布成功!
        echo.
        echo 🔍 测试 TestPyPI 安装...
        echo ⏳ 等待 TestPyPI 更新...
        timeout /t 15 /nobreak >nul
        
        pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ frp-tunnel --upgrade
        
        echo 🔍 测试命令...
        frp-tunnel --version
        
        echo.
        echo ✅ TestPyPI 测试通过!
        echo.
        set /p continue_pypi="TestPyPI 测试成功，是否继续发布到正式 PyPI? (y/n): "
        
        if not "%continue_pypi%"=="y" (
            echo 🛑 用户取消发布到正式 PyPI
            exit /b 0
        )
    ) else (
        echo ❌ TestPyPI 发布失败
        exit /b 1
    )
)

REM 发布到正式 PyPI
echo.
echo 🚀 发布到正式 PyPI...
twine upload dist/*

if %errorlevel% equ 0 (
    echo.
    echo ✅ 成功发布到 PyPI!
    
    REM 测试正式 PyPI 安装
    echo.
    echo 🧪 测试正式 PyPI 安装...
    echo ⏳ 等待 PyPI 更新...
    timeout /t 10 /nobreak >nul
    pip install frp-tunnel --upgrade
    
    echo.
    echo 🔍 测试命令...
    frp-tunnel --version
    
    echo.
    echo 🎉 发布和测试完成!
    echo 📦 包地址: https://pypi.org/project/frp-tunnel/
    echo.
    echo 用户现在可以使用:
    echo   pip install frp-tunnel
    echo   frp-tunnel --help
) else (
    echo ❌ PyPI 发布失败
    exit /b 1
)
