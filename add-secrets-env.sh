#!/bin/bash

# 一键添加所有密钥 (使用环境变量)

echo "🔑 从环境变量添加 GitHub 密钥..."

# 检查环境变量
if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ 请设置 PYPI_TOKEN 环境变量"
    echo "export PYPI_TOKEN='pypi-your-token-here'"
    exit 1
fi

if [ -z "$TEST_PYPI_TOKEN" ]; then
    echo "❌ 请设置 TEST_PYPI_TOKEN 环境变量"  
    echo "export TEST_PYPI_TOKEN='pypi-your-test-token-here'"
    exit 1
fi

# 添加密钥
gh secret set PYPI_API_TOKEN --body "$PYPI_TOKEN"
echo "✅ PYPI_API_TOKEN 已添加"

gh secret set TEST_PYPI_API_TOKEN --body "$TEST_PYPI_TOKEN"
echo "✅ TEST_PYPI_API_TOKEN 已添加"

# 验证密钥
echo "📋 当前密钥列表:"
gh secret list

echo "🎉 完成！现在可以发布包了"
