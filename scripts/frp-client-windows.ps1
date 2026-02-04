# FRP SSH Client for Windows (PowerShell)
#
# 快速开始:
# 1. 先在GCP服务器运行: ./frp-server-gcp.sh
# 2. 复制显示的token
# 3. 在Windows中运行: .\frp-client-windows.ps1 -Token "your_token_here"
# 4. 连接: ssh -p 6001 colab@35.220.164.135
#
# 使用方法:
#   .\frp-client-windows.ps1 -Token "my_token"                                    # 使用默认配置
#   .\frp-client-windows.ps1 -Username "myuser" -RemotePort 6005 -Token "my_token" # 指定参数
#   .\frp-client-windows.ps1 -Token "my_token" -Overwrite                         # 强制重写配置
#
# 参数说明:
#   -Username     用户名 (默认: colab)
#   -RemotePort   端口 (默认: 6001)
#   -ServerAddr   服务器地址 (默认: 35.220.164.135)
#   -Token        认证令牌 (必须提供)
#   -Overwrite    强制重写配置 (开关参数)

param(
    [string]$Username = "colab",
    [int]$RemotePort = 6001,
    [string]$ServerAddr = "35.220.164.135",
    [string]$Token = "",
    [switch]$Overwrite
)

# Check if token is not empty
if ([string]::IsNullOrWhiteSpace($Token)) {
    Write-Host "❌ Error: Token cannot be empty" -ForegroundColor Red
    Write-Host "Usage: .\frp-client-windows.ps1 -Username [user] -RemotePort [port] -ServerAddr [addr] -Token [token] [-Overwrite]" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🚀 FRP SSH Client for Windows" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Yellow
Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "   Username: $Username" -ForegroundColor White
Write-Host "   Remote Port: $RemotePort" -ForegroundColor White
Write-Host "   Server Address: $ServerAddr" -ForegroundColor White
Write-Host "   Auth Token: [Set]" -ForegroundColor White
if ($Overwrite) {
    Write-Host "   Config Mode: Force Overwrite" -ForegroundColor White
} else {
    Write-Host "   Config Mode: Keep Existing" -ForegroundColor White
}
Write-Host "==================================" -ForegroundColor Yellow

# Check if OpenSSH is available
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ OpenSSH not found. Installing..." -ForegroundColor Red
    
    try {
        # Try to install OpenSSH Client using Windows capabilities
        Write-Host "📥 Installing OpenSSH Client..." -ForegroundColor Blue
        Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
        Write-Host "✅ OpenSSH Client installed successfully" -ForegroundColor Green
        
        # Verify installation
        if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
            throw "SSH command still not available after installation"
        }
    } catch {
        Write-Host "❌ Failed to install OpenSSH automatically: $_" -ForegroundColor Red
        Write-Host "📝 Manual installation required:" -ForegroundColor Yellow
        Write-Host "   Settings > Apps > Optional Features > Add Feature > OpenSSH Client" -ForegroundColor White
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Create data directory
$DataDir = "$env:USERPROFILE\data\frp"
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
}
Set-Location $DataDir

# Create frpc configuration
if (-not (Test-Path "frpc.ini") -or $Overwrite) {
    if ($Overwrite) {
        Write-Host "📝 Force overwriting FRP client configuration..." -ForegroundColor Blue
    } else {
        Write-Host "📝 Creating FRP client configuration..." -ForegroundColor Blue
    }
    
    $ConfigContent = @"
[common]
server_addr = $ServerAddr
server_port = 7000
token = $Token

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = $RemotePort
"@
    $ConfigContent | Out-File -FilePath "frpc.ini" -Encoding UTF8
    Write-Host "✅ Configuration port: $RemotePort" -ForegroundColor Green
} else {
    Write-Host "✅ FRP configuration file exists, keeping existing config" -ForegroundColor Green
    Write-Host "💡 Use -Overwrite parameter to force rewrite config" -ForegroundColor Yellow
    
    # Read existing configuration
    $ExistingConfig = Get-Content "frpc.ini"
    $ExistingPort = ($ExistingConfig | Where-Object { $_ -match "remote_port" }) -replace ".*= ", ""
    $ExistingServer = ($ExistingConfig | Where-Object { $_ -match "server_addr" }) -replace ".*= ", ""
    Write-Host "✅ Existing port: $ExistingPort" -ForegroundColor Green
    Write-Host "✅ Existing server: $ExistingServer" -ForegroundColor Green
}

# Download FRP if not exists
$FrpDir = "frp_0.52.3_windows_amd64"
if (-not (Test-Path $FrpDir)) {
    Write-Host "📥 Downloading FRP client..." -ForegroundColor Blue
    $ZipFile = "frp_0.52.3_windows_amd64.zip"
    $Url = "https://github.com/fatedier/frp/releases/download/v0.52.3/$ZipFile"
    
    try {
        Invoke-WebRequest -Uri $Url -OutFile $ZipFile -UseBasicParsing
        Expand-Archive -Path $ZipFile -DestinationPath "." -Force
        Write-Host "✅ FRP client downloaded" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to download FRP client: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "✅ FRP client already downloaded" -ForegroundColor Green
}

# Stop existing frpc process
Get-Process -Name "frpc" -ErrorAction SilentlyContinue | Stop-Process -Force

# Create logs directory
$LogsDir = "$env:USERPROFILE\logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# Start FRP client
Write-Host "🔗 Starting FRP client..." -ForegroundColor Blue
Set-Location $FrpDir
$LogFile = "$LogsDir\frpc.log"
Start-Process -FilePath ".\frpc.exe" -ArgumentList "-c", "..\frpc.ini" -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile -WindowStyle Hidden

Start-Sleep -Seconds 3

# Check if process is running
if (Get-Process -Name "frpc" -ErrorAction SilentlyContinue) {
    Write-Host "✅ FRP client started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ FRP client failed to start" -ForegroundColor Red
    Write-Host "Check log: $LogFile" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🎉 Setup completed!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Yellow
Write-Host "📋 Connection Info:" -ForegroundColor Cyan
Write-Host "   SSH Command: ssh -p $RemotePort $Username@$ServerAddr" -ForegroundColor White
Write-Host "   SSH Config: ssh $Username-$RemotePort (need ~/.ssh/config)" -ForegroundColor White
Write-Host "   Auth Method: RSA Key" -ForegroundColor White
Write-Host "   Key File: $env:USERPROFILE\.ssh\id_rsa" -ForegroundColor White
Write-Host "==================================" -ForegroundColor Yellow
Write-Host "📝 Notes:" -ForegroundColor Cyan
Write-Host "   • Ensure GCP server frps is running" -ForegroundColor White
Write-Host "   • Ensure firewall allows ports 6001-6010,7000" -ForegroundColor White
Write-Host "   • Use RSA key authentication" -ForegroundColor White
Write-Host "   • SSH keys configured automatically" -ForegroundColor White
Write-Host "   • Log file: $LogFile" -ForegroundColor White
Write-Host "==================================" -ForegroundColor Yellow

# Configure SSH keys for passwordless authentication
Write-Host "🔑 Configuring SSH keys..." -ForegroundColor Blue
$SSHDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $SSHDir)) {
    New-Item -ItemType Directory -Path $SSHDir -Force | Out-Null
}

Write-Host "✅ SSH directory ready" -ForegroundColor Green
Write-Host "💡 Add your public key to the Colab server's authorized_keys file" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow

Read-Host "Press Enter to exit"
