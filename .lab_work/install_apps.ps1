$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Open PowerShell as Administrator on Instance-A and run this script again.'
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'
$setupFolder = Join-Path $env:TEMP 'Lab3Installers'
New-Item -ItemType Directory -Path $setupFolder -Force | Out-Null
$everythingSetup = Join-Path $setupFolder 'Everything-1.4.1.1032.x64-Setup.exe'
$wiztreeSetup = Join-Path $setupFolder 'wiztree_4_33_setup.exe'

Invoke-WebRequest -UseBasicParsing -Uri 'https://www.voidtools.com/Everything-1.4.1.1032.x64-Setup.exe' -OutFile $everythingSetup
Invoke-WebRequest -UseBasicParsing -Uri 'https://diskanalyzer.com/files/wiztree_4_33_setup.exe' -OutFile $wiztreeSetup

foreach ($installer in @($everythingSetup, $wiztreeSetup)) {
    $signature = Get-AuthenticodeSignature -LiteralPath $installer
    if ($signature.Status -ne 'Valid') {
        throw "Installer signature check failed: $installer ($($signature.Status))"
    }
    Write-Output "$([IO.Path]::GetFileName($installer)): valid signature from $($signature.SignerCertificate.Subject)"
}

$result = Start-Process -FilePath $everythingSetup -ArgumentList '/S -install-options "-app-data -disable-run-as-admin -install-service -install-desktop-shortcut -install-start-menu-shortcuts" /D=C:\Program Files\Everything' -WindowStyle Hidden -Wait -PassThru
if ($result.ExitCode -ne 0) {
    throw "Everything installation failed with exit code $($result.ExitCode)."
}

$result = Start-Process -FilePath $wiztreeSetup -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /MERGETASKS=desktopicon /DIR="C:\Program Files\WizTree"' -WindowStyle Hidden -Wait -PassThru
if ($result.ExitCode -notin @(0, 3010)) {
    throw "WizTree installation failed with exit code $($result.ExitCode)."
}

$programs = @('C:\Program Files\Everything\Everything.exe', 'C:\Program Files\WizTree\WizTree64.exe')
$names = @('Everything', 'WizTree')
$desktop = [Environment]::GetFolderPath('DesktopDirectory')
$publicDesktop = [Environment]::GetFolderPath('CommonDesktopDirectory')
$shortcutShell = New-Object -ComObject WScript.Shell
for ($i = 0; $i -lt $programs.Count; $i++) {
    if (-not (Test-Path -LiteralPath $programs[$i])) {
        throw "Installed program was not found: $($programs[$i])"
    }
    $shortcutPath = Join-Path $desktop ($names[$i] + '.lnk')
    $publicShortcut = Join-Path $publicDesktop ($names[$i] + '.lnk')
    if (-not (Test-Path -LiteralPath $shortcutPath) -and -not (Test-Path -LiteralPath $publicShortcut)) {
        $shortcut = $shortcutShell.CreateShortcut($publicShortcut)
        $shortcut.TargetPath = $programs[$i]
        $shortcut.Save()
    }
    Get-Item -LiteralPath $programs[$i] | Select-Object Name, @{Name='Version'; Expression={$_.VersionInfo.ProductVersion}}
}

Write-Output 'Installation finished. Open Everything and WizTree from the desktop for the lab screenshot.'
