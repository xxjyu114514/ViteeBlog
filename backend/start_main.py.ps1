# 保存为: activate_env.ps1
# 用途: 自动提权 -> 检查虚拟环境 -> 进入菜单 -> 安装依赖或启动 main.py

# 获取脚本所在目录（这才是你真正的项目目录）
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. 自动提权（请求管理员权限）
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "请求管理员权限..." -ForegroundColor Yellow
    # 关键修复：用 -WorkingDirectory 指定工作目录为脚本所在目录
    Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -Command `"cd '$scriptDir'; & '.\$($MyInvocation.MyCommand.Name)'`""
    exit
}

# 提权后切换到脚本所在目录
Set-Location $scriptDir
Write-Host "已获得管理员权限" -ForegroundColor Green
Write-Host "工作目录: $scriptDir" -ForegroundColor Cyan

# 2. 检查当前目录下是否存在虚拟环境（兼容 .venv 和 venv）
$venvPath = $null
$possiblePaths = @(
    (Join-Path $scriptDir ".venv"),
    (Join-Path $scriptDir "venv")
)

Write-Host "`n正在检查虚拟环境..." -ForegroundColor Cyan

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $scriptsPath = Join-Path $path "Scripts"
        if (Test-Path $scriptsPath) {
            $venvPath = $path
            Write-Host "✓ 找到虚拟环境: $venvPath" -ForegroundColor Green
            break
        }
    }
}

if (-not $venvPath) {
    Write-Host "`n错误: 未找到有效的虚拟环境！" -ForegroundColor Red
    Write-Host "当前目录: $scriptDir" -ForegroundColor Yellow
    Write-Host "当前目录内容:" -ForegroundColor Cyan
    Get-ChildItem -Name -Force
    Write-Host "`n请先创建虚拟环境:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor White
    pause
    exit 1
}

# 3. 激活虚拟环境
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
Write-Host "正在激活虚拟环境..." -ForegroundColor Yellow
& $activateScript

# 4. 显示菜单
do {
    Write-Host "`n=====================================================" -ForegroundColor Cyan
    Write-Host "           虚拟环境管理菜单" -ForegroundColor White
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " 项目目录: $scriptDir" -ForegroundColor DarkGray
    Write-Host " 虚拟环境: $venvPath" -ForegroundColor DarkGray
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " [1] 安装/更新 requirements.txt 中的依赖" -ForegroundColor Yellow
    Write-Host " [2] 启动 main.py" -ForegroundColor Green
    Write-Host " [0] 退出并停用虚拟环境" -ForegroundColor Red
    Write-Host "=====================================================" -ForegroundColor Cyan
    $choice = Read-Host "请输入选项"

    switch ($choice) {
        "1" {
            $reqFile = Join-Path $scriptDir "requirements.txt"
            if (Test-Path $reqFile) {
                Write-Host "`n正在安装依赖..." -ForegroundColor Yellow
                pip install -r $reqFile
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✓ 依赖安装完成！" -ForegroundColor Green
                } else {
                    Write-Host "✗ 安装失败" -ForegroundColor Red
                }
            } else {
                Write-Host "`n✗ 未找到 requirements.txt" -ForegroundColor Red
            }
            Write-Host "`n按任意键返回..." -ForegroundColor DarkGray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "2" {
            $mainFile = Join-Path $scriptDir "main.py"
            if (Test-Path $mainFile) {
                Write-Host "`n正在启动 main.py ..." -ForegroundColor Yellow
                python $mainFile
                Write-Host "`n✓ main.py 执行完毕" -ForegroundColor Green
            } else {
                Write-Host "`n✗ 未找到 main.py" -ForegroundColor Red
            }
            Write-Host "`n按任意键返回..." -ForegroundColor DarkGray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "0" {
            Write-Host "`n正在退出..." -ForegroundColor Yellow
            deactivate 2>$null
            Write-Host "✓ 再见！" -ForegroundColor Green
            break
        }
        default {
            Write-Host "`n✗ 无效选项" -ForegroundColor Red
            Write-Host "`n按任意键继续..." -ForegroundColor DarkGray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
    }
} while ($choice -ne "0")