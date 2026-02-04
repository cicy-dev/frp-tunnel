#!/bin/bash

# 添加 PyPI 密钥脚本

echo "🔑 添加 PyPI API 密钥到 GitHub..."

# 添加生产环境 PyPI token
echo "请输入 PyPI API Token (从 https://pypi.org/manage/account/ 获取):"
read -s PYPI_TOKEN

gh secret set PYPI_API_TOKEN --body "$PYPI_TOKEN"
echo "✅ PYPI_API_TOKEN 已添加"

# 添加测试环境 TestPyPI token  
echo "请输入 TestPyPI API Token (从 https://test.pypi.org/manage/account/ 获取):"
read -s TEST_PYPI_TOKEN

gh secret set TEST_PYPI_API_TOKEN --body "$TEST_PYPI_TOKEN"
echo "✅ TEST_PYPI_API_TOKEN 已添加"

echo "🎉 所有密钥添加完成！"
echo "现在可以使用 GitHub Actions 发布包了"
