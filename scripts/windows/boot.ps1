# SSH Setup Script for Windows
$ErrorActionPreference = "Continue"

# 解析环境变量中的 JSON 数据
Write-Host "Parsing configuration..."
if (-not $env:DATA) {
    Write-Error "DATA environment variable is not set"
    exit 1
}

$result = python scripts/utils/parse-base64-json.py $env:DATA
Write-Host "Raw result: $result"

if (-not $result) {
    Write-Error "Failed to parse JSON data"
    exit 1
}


$json = $result | ConvertFrom-Json

# 调试输出
Write-Host "TEST value: $($json.TEST)"

# 导出为系统环境变量
[System.Environment]::SetEnvironmentVariable("LOGIN_USERNAME", $json.LOGIN_USERNAME, "Machine")
[System.Environment]::SetEnvironmentVariable("LOGIN_PASSWORD", $json.LOGIN_PASSWORD, "Machine")
[System.Environment]::SetEnvironmentVariable("SSH_PUB_KEY_1", $json.SSH_PUB_KEY_1, "Machine")
[System.Environment]::SetEnvironmentVariable("SSH_PUB_KEY_2", $json.SSH_PUB_KEY_2, "Machine")
Write-Host "Environment variables exported globally"

# 验证必需字段
if (-not $json.LOGIN_USERNAME) {
    Write-Error "LOGIN_USERNAME is missing in JSON data"
    exit 1
}
if (-not $json.LOGIN_PASSWORD) {
    Write-Error "LOGIN_PASSWORD is missing in JSON data"
    exit 1
}

Write-Host "Configuration parsed successfully"

# 1. 安装并启动 OpenSSH
Write-Host "Installing OpenSSH..."
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 2. 创建用户
Write-Host "Creating SSH user..."
$username = $json.LOGIN_USERNAME
$password = $json.LOGIN_PASSWORD
$securePass = ConvertTo-SecureString $password -AsPlainText -Force

if (Get-LocalUser -Name $username -ErrorAction SilentlyContinue) {
    Remove-LocalUser -Name $username
}

New-LocalUser -Name $username -Password $securePass -AccountNeverExpires -PasswordNeverExpires | Out-Null
Add-LocalGroupMember -Group "Administrators" -Member $username
Write-Host "Created user: $username"

# 创建 D:\projects 目录
Write-Host "Creating D:\projects directory..."
if (-not (Test-Path "D:\projects")) {
    New-Item -ItemType Directory -Path "D:\projects" -Force | Out-Null
    Write-Host "D:\projects created"
} else {
    Write-Host "D:\projects already exists"
}

# 3. 配置 SSH 公钥（管理员组）
Write-Host "Configuring SSH keys..."
$authKeyPath = "C:\ProgramData\ssh\administrators_authorized_keys"
"$($json.SSH_PUB_KEY_1)`n$($json.SSH_PUB_KEY_2)" | Out-File -FilePath $authKeyPath -Encoding ascii -NoNewline

# 设置权限
$acl = Get-Acl $authKeyPath
$acl.SetAccessRuleProtection($true, $false)
$administrators = New-Object System.Security.Principal.SecurityIdentifier([System.Security.Principal.WellKnownSidType]::BuiltinAdministratorsSid, $null)
$system = New-Object System.Security.Principal.SecurityIdentifier([System.Security.Principal.WellKnownSidType]::LocalSystemSid, $null)
$acl.SetOwner($administrators)
$acl.SetAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule($administrators, "FullControl", "Allow")))
$acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule($system, "FullControl", "Allow")))
Set-Acl $authKeyPath $acl

# 4. 配置 sshd_config
Write-Host "Configuring sshd..."
$sshdConfig = "C:\ProgramData\ssh\sshd_config"
Add-Content $sshdConfig "`nPubkeyAuthentication yes"
Add-Content $sshdConfig "PasswordAuthentication no"
Add-Content $sshdConfig "Match Group administrators"
Add-Content $sshdConfig "       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys"

Restart-Service sshd
Write-Host "SSH setup complete!"

# 5. 以 cicy-dev 用户安装工具
Write-Host "Installing tools as $username user..."
"npm config set prefix C:\Users\$username\AppData\Roaming\npm" | Out-File -FilePath "C:\install-tools.ps1" -Encoding UTF8
"npm install -g electron opencode-ai" | Out-File -FilePath "C:\install-tools.ps1" -Append -Encoding UTF8
"npm list -g --depth=0" | Out-File -FilePath "C:\install-tools.ps1" -Append -Encoding UTF8

$password = ConvertTo-SecureString $json.LOGIN_PASSWORD -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ($username, $password)

Invoke-Command -ComputerName localhost -Credential $cred -ScriptBlock {
    & "C:\install-tools.ps1"
} | Out-Null

Write-Host "Tools installation completed"

Write-Host "`nBoot script completed successfully!"

# 6. 启用 RDP
Write-Host "Enabling RDP..."
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name "fDenyTSConnections" -Value 0 -Force
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name "UserAuthentication" -Value 0 -Force
netsh advfirewall firewall add rule name="RDP" dir=in action=allow protocol=TCP localport=3389
Restart-Service -Name TermService -Force
Add-LocalGroupMember -Group "Remote Desktop Users" -Member $username -ErrorAction SilentlyContinue
Write-Host "RDP enabled for $username"

exit 0

