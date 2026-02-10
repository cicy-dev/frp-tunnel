# SSH Setup Script for Windows
$ErrorActionPreference = "Continue"

# 系统信息检查
Write-Host "`n=== System Information ===" -ForegroundColor Cyan
Write-Host "Username: $env:USERNAME"
Write-Host "Computer: $env:COMPUTERNAME"
Write-Host "Architecture: $env:PROCESSOR_ARCHITECTURE"

# CPU 和内存信息
$cpu = Get-WmiObject Win32_Processor | Select-Object -First 1
$memory = Get-WmiObject Win32_ComputerSystem
Write-Host "CPU: $($cpu.Name)"
Write-Host "Memory: $([math]::Round($memory.TotalPhysicalMemory/1GB, 2)) GB"

# 磁盘信息
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -match '^[CD]$' } | ForEach-Object {
    $used = [math]::Round($_.Used/1GB, 2)
    $free = [math]::Round($_.Free/1GB, 2)
    $total = $used + $free
    Write-Host "Drive $($_.Name): $used GB used / $total GB total"
}

# 公网 IP
Write-Host "Fetching public IP..."
try {
    $ip = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing -TimeoutSec 5).Content
    Write-Host "Public IP: $ip"
} catch {
    Write-Host "Failed to fetch public IP: $($_.Exception.Message)"
}

# Python 版本
Write-Host "Python: $(python --version 2>&1)"
Write-Host "=========================`n" -ForegroundColor Cyan

# 解析环境变量中的 JSON 数据
Write-Host "Parsing configuration..."
if (-not $env:DATA) {
    Write-Error "DATA environment variable is not set"
    exit 1
}

$result = python scripts/utils/parse-base64-json.py $env:DATA
if (-not $result) {
    Write-Error "Failed to parse JSON data"
    exit 1
}


$json = $result | ConvertFrom-Json

# 调试输出
Write-Host "TEST value: $($json.TEST)"

# 导出所有 JSON 字段为系统环境变量
$json.PSObject.Properties | ForEach-Object {
    [System.Environment]::SetEnvironmentVariable($_.Name, $_.Value, "Machine")
    Write-Host "Exported: $($_.Name)"
}
Write-Host "All environment variables exported globally"

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


# 安装本地版本
cd D:\a\frp-tunnel\frp-tunnel
pip install .

# 复制配置文件并替换 token
$configSource = "D:\a\frp-tunnel\frp-tunnel\config\frpc-windows.yaml"
$configDest = "$env:USERPROFILE\data\frp\frpc.yaml"
New-Item -ItemType Directory -Force -Path (Split-Path $configDest) | Out-Null
(Get-Content $configSource) -replace 'REPLACE_WITH_TOKEN', $env:FRP_TOKEN | Set-Content $configDest

# 下载 FRP 二进制文件
python -c "from frp_tunnel.cli import download_frp; download_frp()"

# 使用 PowerShell Job 在后台运行 frpc.exe
$frpcExe = "$env:USERPROFILE\.frp-tunnel\bin\frpc.exe"
$job = Start-Job -ScriptBlock {
    param($exe, $config)
    & $exe -c $config
} -ArgumentList $frpcExe, $configDest

Write-Host "FRP client started in background job (ID: $($job.Id))"
Start-Sleep -Seconds 1

# Keep alive loop with monitoring
$monitorFile = "C:\running.txt"
New-Item -Path $monitorFile -ItemType File -Force | Out-Null
$startTime = Get-Date
$runDuration = New-TimeSpan -Hours 5 -Minutes 30

while ($true) {
    Write-Host "=======================================`n"
    Write-Host "[$(Get-Date)] Monitoring started. Checking monitor file...`n"

    if (-not (Test-Path -Path $monitorFile -PathType Leaf)) {
        Write-Host "`n======================================="
        Write-Host "[$(Get-Date)] ERROR: Monitor file $monitorFile not found!"
        Write-Host "[$(Get-Date)] Stopping monitoring and exiting loop."
        Write-Host "=======================================`n"
        break
    }

    $elapsedTime = (Get-Date) - $startTime
    if ($elapsedTime -gt $runDuration) {
        Write-Host "`n======================================="
        Write-Host "[$(Get-Date)] Runtime limit reached (5h30m)."
        Write-Host "[$(Get-Date)] Stopping monitoring."
        Write-Host "=======================================`n"
        break
    }

    Write-Host "`n--- FRP Client Status ---"
    ft client-status
    Write-Host "-------------------------`n"

    Write-Host "`n======================================="
    Write-Host "[$(Get-Date)] Active - Runtime: $($elapsedTime.ToString('hh\:mm\:ss'))"
    Write-Host "[$(Get-Date)] Monitor file exists: $monitorFile"
    Write-Host "[$(Get-Date)] Next check in 50 seconds (Ctrl+C to terminate)"
    Write-Host "=======================================`n`n"

    Start-Sleep -Seconds 50
}

Write-Host "Session completed."


