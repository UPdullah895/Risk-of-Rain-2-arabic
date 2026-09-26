<#
    Risk of Rain 2 in Arabic - installer.

    Double-click install-windows.bat, which runs this. It draws a small window, finds the
    game, and copies the mod into BepInEx/plugins. Uninstalling deletes the folder it
    copied and leaves the game exactly as it was.

    Nothing has to be installed first: Windows ships both PowerShell and WinForms. BepInEx
    does have to be there already, and the window says so if it is not.
#>

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

# The window is launched hidden, so anything that escapes a handler has to say so itself.
trap {
    [System.Windows.Forms.MessageBox]::Show(
        "$_", 'Risk of Rain 2 Arabic installer', 'OK', 'Error') | Out-Null
    exit 1
}

$AppId = '632360'
$Mod   = 'RoR2Arabic'
$Exe   = 'Risk of Rain 2.exe'
$Here  = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }

# --- finding the game ------------------------------------------------------------------

function Test-Game([string]$dir) {
    if ([string]::IsNullOrWhiteSpace($dir)) { return $false }
    return (Test-Path (Join-Path $dir $Exe)) -or (Test-Path (Join-Path $dir 'Risk of Rain 2_Data'))
}

function Test-BepInEx([string]$dir) {
    return (Test-Path (Join-Path $dir 'BepInEx\core\BepInEx.dll'))
}

function Get-SteamRoots {
    $roots = New-Object System.Collections.Generic.List[string]
    foreach ($key in @('HKCU:\Software\Valve\Steam',
                       'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam',
                       'HKLM:\SOFTWARE\Valve\Steam')) {
        try {
            $item = Get-ItemProperty -Path $key -ErrorAction Stop
            foreach ($name in @('SteamPath', 'InstallPath')) {
                if ($item.$name) { $roots.Add([string]$item.$name) }
            }
        } catch { }
    }
    foreach ($p in @("${env:ProgramFiles(x86)}\Steam", "$env:ProgramFiles\Steam", 'C:\Steam')) {
        if ($p) { $roots.Add($p) }
    }
    return ($roots | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique)
}

# Steam keeps its library list in a Valve key-value file. Pulling the "path" lines out of it
# is enough; a full parser is not worth it for one field. Paths in it are backslash-escaped.
function Get-SteamLibraries([string]$root) {
    $libs = @($root)
    $vdf = Join-Path $root 'steamapps\libraryfolders.vdf'
    if (Test-Path $vdf) {
        foreach ($m in [regex]::Matches((Get-Content -Raw -LiteralPath $vdf), '"path"\s*"([^"]+)"')) {
            $libs += ($m.Groups[1].Value -replace '\\\\', '\')
        }
    }
    return $libs
}

function Find-Game {
    foreach ($root in Get-SteamRoots) {
        foreach ($lib in Get-SteamLibraries $root) {
            if (-not $lib -or -not (Test-Path $lib)) { continue }
            $installdir = 'Risk of Rain 2'
            $manifest = Join-Path $lib "steamapps\appmanifest_$AppId.acf"
            if (Test-Path $manifest) {
                $m = [regex]::Match((Get-Content -Raw -LiteralPath $manifest), '"installdir"\s*"([^"]+)"')
                if ($m.Success) { $installdir = $m.Groups[1].Value }
            }
            $dir = Join-Path $lib "steamapps\common\$installdir"
            if (Test-Game $dir) { return $dir }
        }
    }
    return $null
}

function Get-Payload {
    foreach ($d in @((Join-Path $Here $Mod), (Join-Path $Here "dist\$Mod"))) {
        if (Test-Path (Join-Path $d "$Mod.dll")) { return $d }
    }
    return $null
}

# --- the window ------------------------------------------------------------------------

$form                   = New-Object System.Windows.Forms.Form
$form.Text              = 'تعريب Risk of Rain 2'
$form.ClientSize        = New-Object System.Drawing.Size(600, 230)
$form.FormBorderStyle   = 'FixedDialog'
$form.MaximizeBox       = $false
$form.StartPosition     = 'CenterScreen'
$form.RightToLeft       = 'Yes'
$form.RightToLeftLayout = $true
$form.Font              = New-Object System.Drawing.Font('Segoe UI', 10)

$label          = New-Object System.Windows.Forms.Label
$label.Text     = 'مجلد اللعبة (الذي يحتوي على Risk of Rain 2.exe):'
$label.Location = New-Object System.Drawing.Point(20, 18)
$label.Size     = New-Object System.Drawing.Size(560, 24)
$form.Controls.Add($label)

$path          = New-Object System.Windows.Forms.TextBox
$path.Location = New-Object System.Drawing.Point(130, 46)
$path.Size     = New-Object System.Drawing.Size(450, 26)
$form.Controls.Add($path)

$browse          = New-Object System.Windows.Forms.Button
$browse.Text     = 'استعراض...'
$browse.Location = New-Object System.Drawing.Point(20, 45)
$browse.Size     = New-Object System.Drawing.Size(100, 28)
$form.Controls.Add($browse)

$status           = New-Object System.Windows.Forms.Label
$status.Location  = New-Object System.Drawing.Point(20, 84)
$status.Size      = New-Object System.Drawing.Size(560, 76)
$form.Controls.Add($status)

$install          = New-Object System.Windows.Forms.Button
$install.Text     = 'تثبيت'
$install.Location = New-Object System.Drawing.Point(440, 178)
$install.Size     = New-Object System.Drawing.Size(140, 34)
$form.Controls.Add($install)

$uninstall          = New-Object System.Windows.Forms.Button
$uninstall.Text     = 'إزالة'
$uninstall.Location = New-Object System.Drawing.Point(290, 178)
$uninstall.Size     = New-Object System.Drawing.Size(140, 34)
$form.Controls.Add($uninstall)

$close          = New-Object System.Windows.Forms.Button
$close.Text     = 'إغلاق'
$close.Location = New-Object System.Drawing.Point(20, 178)
$close.Size     = New-Object System.Drawing.Size(100, 34)
$form.Controls.Add($close)

function Set-Status([string]$text, [string]$colour) {
    $status.Text      = $text
    $status.ForeColor = [System.Drawing.Color]::FromName($colour)
}

# --- what the buttons do ----------------------------------------------------------------

$browse.Add_Click({
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = 'اختر مجلد Risk of Rain 2'
    if ($path.Text -and (Test-Path $path.Text)) { $dialog.SelectedPath = $path.Text }
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $path.Text = $dialog.SelectedPath
        if (Test-Game $dialog.SelectedPath) {
            Set-Status 'تم العثور على اللعبة.' 'DarkGreen'
        } else {
            Set-Status 'لا يوجد Risk of Rain 2.exe في هذا المجلد.' 'Firebrick'
        }
    }
})

$install.Add_Click({
    $game = $path.Text
    if (-not (Test-Game $game)) {
        Set-Status 'لا يوجد Risk of Rain 2.exe في هذا المجلد. اختر مجلد اللعبة الصحيح.' 'Firebrick'
        return
    }
    if (-not (Test-BepInEx $game)) {
        Set-Status ("BepInEx غير مثبّت في مجلد اللعبة، والتعريب إضافة تعمل من خلاله.`n" +
                    "نزّل BepInEx 5.4.21 (x64) وفك ضغطه داخل مجلد اللعبة بحيث يصير مجلد`n" +
                    "BepInEx بجوار Risk of Rain 2.exe، ثم أعد تشغيل هذا المثبّت.") 'Firebrick'
        return
    }
    $payload = Get-Payload
    if (-not $payload) {
        Set-Status "ملفات التعريب غير موجودة بجانب هذا المثبّت.`nشغّله من داخل مجلد الإصدار كما نُزّل." 'Firebrick'
        return
    }
    $target = Join-Path $game "BepInEx\plugins\$Mod"
    try {
        if (Test-Path $target) { Remove-Item -LiteralPath $target -Recurse -Force }
        New-Item -ItemType Directory -Force -Path $target | Out-Null
        Copy-Item -Path (Join-Path $payload '*') -Destination $target -Recurse -Force
        Set-Status "تم التثبيت.`nشغّل اللعبة، ثم اختر العربية من قائمة اللغات في الإعدادات." 'DarkGreen'
    } catch [System.UnauthorizedAccessException] {
        Set-Status "لا توجد صلاحية للكتابة في مجلد اللعبة.`nأغلق النافذة وشغّل المثبّت كمسؤول (زر الفأرة الأيمن > تشغيل كمسؤول)." 'Firebrick'
    } catch {
        Set-Status ("تعذّر التثبيت: " + $_.Exception.Message) 'Firebrick'
    }
})

$uninstall.Add_Click({
    $game = $path.Text
    if (-not (Test-Game $game)) {
        Set-Status 'لا يوجد Risk of Rain 2.exe في هذا المجلد.' 'Firebrick'
        return
    }
    $target = Join-Path $game "BepInEx\plugins\$Mod"
    if (-not (Test-Path $target)) {
        Set-Status 'التعريب غير مثبّت أصلًا.' 'DimGray'
        return
    }
    try {
        Remove-Item -LiteralPath $target -Recurse -Force
        Set-Status 'تمت الإزالة. عادت اللعبة إلى الإنجليزية.' 'DarkGreen'
    } catch {
        Set-Status ("تعذّرت الإزالة: " + $_.Exception.Message) 'Firebrick'
    }
})

$close.Add_Click({ $form.Close() })

$found = Find-Game
if ($found) {
    $path.Text = $found
    if (Test-BepInEx $found) {
        Set-Status 'تم العثور على اللعبة. اضغط "تثبيت".' 'DarkGreen'
    } else {
        Set-Status ("تم العثور على اللعبة، لكن BepInEx غير مثبّت فيها.`n" +
                    "نزّل BepInEx 5.4.21 (x64) وفك ضغطه داخل مجلد اللعبة، ثم أعد التشغيل.") 'Firebrick'
    }
} else {
    Set-Status "لم يُعثر على اللعبة تلقائيًا.`nاضغط ""استعراض..."" وحدّد المجلد الذي يحتوي على Risk of Rain 2.exe." 'Firebrick'
}

[void]$form.ShowDialog()
