# SSH Setup Script for Windows
$ErrorActionPreference = "Continue"

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
Add-Content $sshdConfig "Match User $username"
Add-Content $sshdConfig "       ForceCommand powershell.exe -NoProfile -Command `"Set-Location D:\projects; powershell.exe -NoExit`""

Restart-Service sshd
Write-Host "SSH setup complete!"

# 5. 以 cicy-dev 用户安装工具
Write-Host "Installing tools as cicy-dev user..."
"npm config set prefix C:\Users\$username\AppData\Roaming\npm" | Out-File -FilePath "C:\install-tools.ps1" -Encoding UTF8
"npm install -g electron opencode-ai" | Out-File -FilePath "C:\install-tools.ps1" -Append -Encoding UTF8
"npm list -g --depth=0" | Out-File -FilePath "C:\install-tools.ps1" -Append -Encoding UTF8

$password = ConvertTo-SecureString "P@ssw0rd123!" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ($username, $password)

Invoke-Command -ComputerName localhost -Credential $cred -ScriptBlock {
    & "C:\install-tools.ps1"
}

Write-Host "Tools installation completed"

Write-Host "`nBoot script completed successfully!"
exit 0

