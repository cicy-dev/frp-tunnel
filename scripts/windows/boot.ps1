# SSH Setup Script for Windows

# 1. 安装并启动 OpenSSH
Write-Host "Installing OpenSSH..."
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 2. 创建用户
Write-Host "Creating SSH user..."
$username = if ($env:SSH_USERNAME) { $env:SSH_USERNAME } else { "cicy-dev" }
$password = "P@ssw0rd123!"
$securePass = ConvertTo-SecureString $password -AsPlainText -Force

if (Get-LocalUser -Name $username -ErrorAction SilentlyContinue) {
    Remove-LocalUser -Name $username
}

New-LocalUser -Name $username -Password $securePass -AccountNeverExpires -PasswordNeverExpires
Add-LocalGroupMember -Group "Administrators" -Member $username
Write-Host "Created user: $username"

# 3. 配置 SSH 公钥（管理员组）
Write-Host "Configuring SSH keys..."
$authKeyPath = "C:\ProgramData\ssh\administrators_authorized_keys"
"$env:PUBLIC_KEY_1`n$env:PUBLIC_KEY_2" | Out-File -FilePath $authKeyPath -Encoding ascii

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

# 5. 检查并安装 Electron
Write-Host "Checking Electron..."
$electronInstalled = npm list -g electron 2>$null
if (-not $electronInstalled) {
    Write-Host "Installing Electron globally..."
    npm install -g electron
} else {
    Write-Host "Electron already installed"
}

# 6. 检查并安装 OpenCode AI
Write-Host "Checking OpenCode AI..."
$opencodeInstalled = npm list -g opencode-ai 2>$null
if (-not $opencodeInstalled) {
    Write-Host "Installing OpenCode AI globally..."
    npm install -g opencode-ai
} else {
    Write-Host "OpenCode AI already installed"
}

# 7. 显示版本信息
Write-Host "`n=== Installed Versions ==="
electron -v
opencode -v
