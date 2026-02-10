import os
import json
import base64
import subprocess
import sys

"""
python env-to-base64.py $GH_TOKEN_CICYBOT frp-tunnel
"""

print("用法: python env-to-base64.py <github_token> <repo>\n")

# 使用 token 登录 gh
try:
    
    json_data = {
        "TEST": "V1",
        "LOGIN_USERNAME": os.getenv("LOGIN_USERNAME"),
        "LOGIN_PASSWORD": os.getenv("LOGIN_PASSWORD"),
        "SSH_PUB_KEY_1": os.getenv("SSH_PUB_KEY_1"),
        "SSH_PUB_KEY_2": os.getenv("SSH_PUB_KEY_2"),
    }
    print("DATA:")
    print(json_data)

    json_str = json.dumps(json_data)
    base64_result = base64.b64encode(json_str.encode()).decode()

    print(base64_result)

    if len(sys.argv) == 3:

        token = sys.argv[1]
        repo = sys.argv[2]

        process = subprocess.Popen(['gh', 'auth', 'login', '--with-token'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        stdout, stderr = process.communicate(input=token)

        if process.returncode != 0:
            print(f"gh 登录失败: {stderr}")
            sys.exit(1)

        print("gh 登录成功")
        

        # 设置 GitHub secret
        result = subprocess.run(['gh', 'secret', 'set', 'DATA', '--body', base64_result, '--repo', repo], 
                            capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"设置 secret 失败: {result.stderr}")
            print(f"stdout: {result.stdout}")
            sys.exit(1)
        
        print(f"已设置 DATA secret 到 {repo}: {base64_result}")

except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)
