#!/bin/bash

# 一键发布到 PyPI 脚本
set -e

echo "🚀 一键发布 frp-tunnel 到 PyPI"
echo "=============================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否在 GitHub Actions 环境
if [ -n "$GITHUB_ACTIONS" ]; then
    echo "🤖 检测到 GitHub Actions 环境"
    # GitHub Actions 使用 secrets，不需要手动输入
    if [ -z "$PYPI_API_TOKEN" ] || [ -z "$TEST_PYPI_API_TOKEN" ]; then
        echo "❌ GitHub Actions 需要设置 PYPI_API_TOKEN 和 TEST_PYPI_API_TOKEN secrets"
        exit 1
    fi
else
    echo "💻 本地环境 - 需要输入令牌"
    
    # 检查是否有令牌文件
    if [ ! -f ~/.pypirc ] || ! grep -q "password" ~/.pypirc 2>/dev/null; then
        echo ""
        echo "📝 需要设置 PyPI 令牌"
        echo "请输入你的 TestPyPI API 令牌 (以 pypi- 开头):"
        read -s TEST_PYPI_TOKEN
        
        echo "请输入你的 PyPI API 令牌 (以 pypi- 开头):"
        read -s PYPI_TOKEN
        
        cat > ~/.pypirc << EOF
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = $PYPI_TOKEN

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = $TEST_PYPI_TOKEN
EOF
        chmod 600 ~/.pypirc
        echo "✅ PyPI 令牌已保存"
        # 设置 GitHub secrets
        echo ""
        echo "🔐 设置 GitHub secrets..."
        if command -v gh >/dev/null 2>&1; then
            echo "$PYPI_TOKEN" | gh secret set PYPI_API_TOKEN
            echo "$TEST_PYPI_TOKEN" | gh secret set TEST_PYPI_API_TOKEN
            echo "✅ GitHub secrets 已设置"
        else
            echo "⚠️  未找到 gh CLI，请手动设置 GitHub secrets:"
            echo "   - PYPI_API_TOKEN"
            echo "   - TEST_PYPI_API_TOKEN"
            echo "   在: https://github.com/cicy-dev/frp-tunnel/settings/secrets/actions"
        fi
    else
        echo "✅ 找到现有的 PyPI 配置"
    fi
fi

# 构建包
echo ""
echo "📦 构建包..."
rm -rf dist/*
source build_env/bin/activate
python -m build

echo ""
echo "📋 构建的包："
ls -la dist/

# 本地环境：先发布到 TestPyPI 测试
if [ -z "$GITHUB_ACTIONS" ]; then
    echo ""
    echo "🧪 本地环境 - 先发布到 TestPyPI 测试..."
    twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        echo "✅ TestPyPI 发布成功!"
        echo ""
        echo "🔍 测试 TestPyPI 安装..."
        
        # 创建临时测试环境
        TEST_ENV="/tmp/frp_test_$$"
        python3 -m venv "$TEST_ENV"
        source "$TEST_ENV/bin/activate"
        
        # 等待 TestPyPI 更新
        echo "⏳ 等待 TestPyPI 更新..."
        sleep 15
        
        # 从 TestPyPI 安装测试
        pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ frp-tunnel --upgrade
        
        echo "🔍 测试命令..."
        frp-tunnel --version
        frp-tunnel --help | head -5
        
        # 清理测试环境
        deactivate
        rm -rf "$TEST_ENV"
        
        echo ""
        echo "✅ TestPyPI 测试通过!"
        echo ""
        read -p "TestPyPI 测试成功，是否继续发布到正式 PyPI? (y/n): " continue_pypi
        
        if [ "$continue_pypi" != "y" ]; then
            echo "🛑 用户取消发布到正式 PyPI"
            exit 0
        fi
    else
        echo "❌ TestPyPI 发布失败"
        exit 1
    fi
fi

# 发布到正式 PyPI
echo ""
echo "🚀 发布到正式 PyPI..."
twine upload dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 成功发布到 PyPI!"
    
    # 测试正式 PyPI 安装
    echo ""
    echo "🧪 测试正式 PyPI 安装..."
    
    # 创建临时测试环境
    TEST_ENV="/tmp/frp_test_$$"
    python3 -m venv "$TEST_ENV"
    source "$TEST_ENV/bin/activate"
    
    # 等待 PyPI 更新
    echo "⏳ 等待 PyPI 更新..."
    sleep 10
    
    # 安装并测试
    pip install frp-tunnel --upgrade
    
    echo ""
    echo "🔍 测试命令..."
    frp-tunnel --version
    frp-tunnel --help | head -5
    
    # 清理测试环境
    deactivate
    rm -rf "$TEST_ENV"
    
    echo ""
    echo "🎉 发布和测试完成！"
    echo "📦 包地址: https://pypi.org/project/frp-tunnel/"
    echo ""
    echo "用户现在可以使用："
    echo "  pip install frp-tunnel"
    echo "  frp-tunnel --help"
else
    echo "❌ PyPI 发布失败"
    exit 1
fi
