[CmdletBinding()]
param(
    [string]$EntryScript = 'launcher.py'
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$appRootPath = $PSScriptRoot
$bootstrapLogPath = Join-Path $appRootPath 'Python自动安装错误.log'

function Test-PythonRuntime {
    param([string]$ExecutablePath)

    if ([string]::IsNullOrWhiteSpace($ExecutablePath) -or
        -not (Test-Path -LiteralPath $ExecutablePath -PathType Leaf)) {
        return $false
    }
    if ($ExecutablePath -like '*\WindowsApps\*') {
        return $false
    }
    try {
        & $ExecutablePath -I -B -c "import tkinter, ssl, json" 2>$null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

function Find-SystemPython {
    foreach ($commandName in @('python.exe', 'python3.exe')) {
        $commands = @(Get-Command $commandName -All -ErrorAction SilentlyContinue)
        foreach ($command in $commands) {
            $candidatePath = [string]$command.Source
            if (Test-PythonRuntime $candidatePath) {
                return $candidatePath
            }
        }
    }

    $pythonLauncher = Get-Command 'py.exe' -ErrorAction SilentlyContinue
    if ($null -ne $pythonLauncher) {
        try {
            $candidatePath = (& $pythonLauncher.Source -3 -c "import sys; print(sys.executable)" 2>$null |
                Select-Object -First 1)
            if (Test-PythonRuntime ([string]$candidatePath)) {
                return [string]$candidatePath
            }
        }
        catch {
        }
    }
    return $null
}

function Install-OfficialPython {
    $localAppDataPath = [Environment]::GetFolderPath('LocalApplicationData')
    if ([string]::IsNullOrWhiteSpace($localAppDataPath)) {
        throw '无法确定当前用户的 LocalAppData 目录。'
    }

    $architectureName = [string]$env:PROCESSOR_ARCHITEW6432
    if ([string]::IsNullOrWhiteSpace($architectureName)) {
        $architectureName = [string]$env:PROCESSOR_ARCHITECTURE
    }
    $architectureName = $architectureName.ToUpperInvariant()

    switch ($architectureName) {
        'ARM64' {
            $installerFileName = 'python-3.11.9-arm64.exe'
            $runtimeFolderName = 'Python311-arm64'
        }
        'AMD64' {
            $installerFileName = 'python-3.11.9-amd64.exe'
            $runtimeFolderName = 'Python311-amd64'
        }
        default {
            $installerFileName = 'python-3.11.9.exe'
            $runtimeFolderName = 'Python311-win32'
        }
    }

    $runtimeCachePath = Join-Path $localAppDataPath 'BinanceCopySlotIndependent'
    $installTargetPath = Join-Path $runtimeCachePath $runtimeFolderName
    $installedPythonPath = Join-Path $installTargetPath 'python.exe'
    if (Test-PythonRuntime $installedPythonPath) {
        return $installedPythonPath
    }

    New-Item -ItemType Directory -Force -Path $runtimeCachePath | Out-Null
    $installerPath = Join-Path $runtimeCachePath $installerFileName
    $downloadUrl = 'https://www.python.org/ftp/python/3.11.9/' + $installerFileName

    Write-Host '未找到可用的 Python，正在从 Python 官方网站自动下载……' -ForegroundColor Yellow
    Write-Host $downloadUrl
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing

    $downloadedFile = Get-Item -LiteralPath $installerPath
    if ($downloadedFile.Length -lt 20000000) {
        throw '下载的 Python 安装包大小异常，已停止安装。'
    }

    $signature = Get-AuthenticodeSignature -FilePath $installerPath
    $signerSubject = if ($null -ne $signature.SignerCertificate) {
        [string]$signature.SignerCertificate.Subject
    }
    else {
        ''
    }
    if ($signature.Status -ne 'Valid' -or
        $signerSubject -notmatch 'Python Software Foundation') {
        throw ('Python 安装包数字签名验证失败。状态：{0}，签名者：{1}' -f
            $signature.Status, $signerSubject)
    }

    Write-Host '下载完成，正在为当前用户安装 Python……' -ForegroundColor Yellow
    $installerArguments = @(
        '/quiet',
        'InstallAllUsers=0',
        ('TargetDir="{0}"' -f $installTargetPath),
        'Include_exe=1',
        'Include_lib=1',
        'Include_tcltk=1',
        'Include_pip=0',
        'Include_launcher=0',
        'Include_test=0',
        'Include_doc=0',
        'Include_dev=0',
        'AssociateFiles=0',
        'Shortcuts=0',
        'PrependPath=0'
    )
    $installerProcess = Start-Process -FilePath $installerPath `
        -ArgumentList $installerArguments -Wait -PassThru
    if ($installerProcess.ExitCode -notin @(0, 3010)) {
        throw ('Python 安装失败，安装程序退出代码：{0}' -f $installerProcess.ExitCode)
    }
    if (-not (Test-PythonRuntime $installedPythonPath)) {
        throw 'Python 已安装，但图形组件或网络组件无法加载。'
    }
    Write-Host 'Python 自动安装完成。' -ForegroundColor Green
    return $installedPythonPath
}

try {
    if (-not (Test-Path -LiteralPath (Join-Path $appRootPath $EntryScript) -PathType Leaf)) {
        throw ('入口文件不存在：{0}' -f $EntryScript)
    }

    $portablePythonPath = Join-Path $appRootPath 'py\python.exe'
    if (Test-PythonRuntime $portablePythonPath) {
        $selectedPythonPath = $portablePythonPath
    }
    else {
        $selectedPythonPath = Find-SystemPython
        if ([string]::IsNullOrWhiteSpace([string]$selectedPythonPath)) {
            $selectedPythonPath = Install-OfficialPython
        }
    }

    Push-Location $appRootPath
    try {
        & $selectedPythonPath -I -B (Join-Path $appRootPath $EntryScript)
        $programExitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    exit $programExitCode
}
catch {
    $errorDetails = @(
        ('时间：{0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')),
        ('错误：{0}' -f $_.Exception.Message),
        '',
        ($_ | Out-String)
    ) -join [Environment]::NewLine
    [IO.File]::WriteAllText($bootstrapLogPath, $errorDetails, [Text.Encoding]::UTF8)
    Write-Host ''
    Write-Host ('启动失败：{0}' -f $_.Exception.Message) -ForegroundColor Red
    Write-Host ('详细信息已保存到：{0}' -f $bootstrapLogPath)
    exit 1
}
