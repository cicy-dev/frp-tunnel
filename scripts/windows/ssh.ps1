# SSH Setup Script for Windows

# 1. 安装并启动 OpenSSH
Write-Host "Installing OpenSSH..."
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 2. 创建用户
Write-Host "Creating SSH user..."
$password = "P@ssw0rd123!"
$securePass = ConvertTo-SecureString $password -AsPlainText -Force

if (Get-LocalUser -Name "sshuser" -ErrorAction SilentlyContinue) {
    Remove-LocalUser -Name "sshuser"
}

New-LocalUser -Name "sshuser" -Password $securePass -AccountNeverExpires -PasswordNeverExpires
Add-LocalGroupMember -Group "Administrators" -Member "sshuser"

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
