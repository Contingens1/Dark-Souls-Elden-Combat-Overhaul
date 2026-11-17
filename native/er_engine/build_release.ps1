# Builds the distributable package "ER-Inspired DSR Remake":
#   dist\release\ER-Inspired_DSR_Remake_v<Version>\  and  dist\release\ER-Inspired_DSR_Remake_v<Version>.zip
# Contents: release DLL (/DER_DIAG=0, no diagnostics), game files for Mod Engine 2, the end-user setup tool
# (Setup.bat + setup\Setup.ps1; called "Konfiguracja" in the UI - it installs nothing) and README. No third-party DLLs are bundled.
# Since 1.3 the Artorias boss rework (dev package dist\mods\bossy_nightreign\files_c4100_v2, docs\PLAN_PROJEKTU.md
# section 6a) ships inside files\: its anibnd and map AI script are added, and its GameParam (= the main mod's
# GameParam + the boss rows, built by tools\artorias_phase2.py) replaces the main one. The DLL turns the boss
# logic on when files\chr\c4100.anibnd.dcx is present ([Bosses] ArtoriasPhase2=2).
# Since 0.5.4 two more reworked bosses ship as test versions (game files only, no DLL logic, no params): Capra Demon
# with Omen Killer attacks from Elden Ring (dev package files_c2240_omen) and Gaping Dragon with an AI modelled on
# Nightreign (files_c5260_ai: anibnd + the Depths map AI script m10_00).
# Since 0.5.5: Gwyn with two phases as a third boss in testing (files_c5370_p2: anibnd + the Kiln map AI script
# m18_00; the DLL turns phase 2 on when files\chr\c5370.anibnd.dcx is present), so the GameParam now comes from the
# shared boss package files_bosses_param (main GameParam + Artorias rows + Gwyn rows, tools\boss_gameparam.py).
# Also since 0.5.5 a tester DLL bin\er_engine_diag.dll (/DER_DIAG=2: log + F8, no developer keys, no .text dump) with
# its own config ER-Inspired_DSR_Remake_logs.toml and launcher Launch_with_logs.bat; the main DLL stays /DER_DIAG=0.
# setup\Setup.sh = the Linux setup (experimental, Steam + Proton).
# -DllSource builds the DLL from another er_engine.cpp (e.g. a clean worktree of main) when the working folder holds
# uncommitted experiments; its folder must hold the headers it includes.
# Usage: powershell -ExecutionPolicy Bypass -File native\er_engine\build_release.ps1 [-Version 0.4.0] [-DllSource <path>] [-SkipInstallerTest]
param(
    [string]$Version = '0.5.6',
    [string]$Repo = 'Contingens1/Dark-Souls-Elden-Combat-Overhaul',   # GitHub repo whose latest release setup\Update.ps1 checks
    [string]$DllSource = '',
    [switch]$SkipInstallerTest
)
$ErrorActionPreference = 'Stop'
$root = Split-Path (Split-Path $PSScriptRoot)
$fileBase = 'ER-Inspired_DSR_Remake'
$name = "${fileBase}_v$Version"
$out = Join-Path $root "dist\release\$name"
$mh = 'C:\Users\nemos\workspace\toolsy\minhook'
$dev = Join-Path $root 'dist\mods\c0000_er_engine'
$devBoss = Join-Path $root 'dist\mods\bossy_nightreign\files_c4100_v2'
$bossFiles = @('chr\c4100.anibnd.dcx', 'script\m12_01_00_00.luabnd.dcx')
# Shared boss GameParam (main + Artorias + Gwyn rows). boss_rows.txt names the sources it was built from.
$devBossParam = Join-Path $root 'dist\mods\bossy_nightreign\files_bosses_param'
$testBossFiles = [ordered]@{   # file in files\ -> dev folder it comes from (bosses in testing, see the header)
    'chr\c2240.anibnd.dcx'           = 'dist\mods\bossy_nightreign\files_c2240_omen'
    'chr\c5260.anibnd.dcx'           = 'dist\mods\bossy_nightreign\files_c5260_ai'
    'script\m10_00_00_00.luabnd.dcx' = 'dist\mods\bossy_nightreign\files_c5260_ai'
    'chr\c5370.anibnd.dcx'           = 'dist\mods\bossy_nightreign\files_c5370_p2'
    'script\m18_00_00_00.luabnd.dcx' = 'dist\mods\bossy_nightreign\files_c5370_p2'
}
if (-not $DllSource) { $DllSource = Join-Path $PSScriptRoot 'er_engine.cpp' }
if (-not (Test-Path $DllSource)) { throw "DLL source not found: $DllSource" }
$DllSource = (Resolve-Path $DllSource).Path
$devModEngine2 = 'C:\Users\nemos\workspace\toolsy\ModEngine2'   # only for the installer test at the end
# DarkSoulsRemastered.exe the hooks were made for (docs\PLAN_PROJEKTU.md, section 3). The setup tool compares it.
$exeSha256 = 'A45AAA36DD2F6CC151670A639EA5547043CF38EA79FF4178B963C6ED71F98D7B'
$utf8Bom = New-Object System.Text.UTF8Encoding($true)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

if (Test-Path $out) { Remove-Item -Recurse -Force $out }
New-Item -ItemType Directory -Force "$out\bin", "$out\files", "$out\setup", "$out\obj" | Out-Null

# 1. Release DLL (ER_DIAG=0).
$vcvars = 'C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
$cl = "cl /nologo /O2 /MT /W3 /EHsc /LD /DER_DIAG=0 /I`"$mh\include`" `"$DllSource`" `"$mh\src\buffer.c`" `"$mh\src\hook.c`" `"$mh\src\trampoline.c`" `"$mh\src\hde\hde64.c`" /Fo`"$out\obj\\`" /Fe`"$out\bin\er_engine.dll`" /link /DEF:`"$PSScriptRoot\dinput8.def`" user32.lib"
cmd /c "`"$vcvars`" >nul && $cl" | Select-String 'error' | ForEach-Object { throw "Compile error: $_" }
Remove-Item -Recurse -Force "$out\obj"
# Tester DLL (ER_DIAG=2): the same source with the log and F8 only, used by Launch_with_logs.bat.
New-Item -ItemType Directory -Force "$out\obj" | Out-Null
$clDiag = $cl.Replace('/DER_DIAG=0', '/DER_DIAG=2').Replace("$out\bin\er_engine.dll", "$out\bin\er_engine_diag.dll")
cmd /c "`"$vcvars`" >nul && $clDiag" | Select-String 'error' | ForEach-Object { throw "Compile error (tester DLL): $_" }
Remove-Item -Recurse -Force "$out\obj"
Get-ChildItem "$out\bin" -Exclude er_engine.dll, er_engine_diag.dll | Remove-Item -Force
if (-not (Test-Path "$out\bin\er_engine.dll")) { throw 'er_engine.dll was not built.' }
if (-not (Test-Path "$out\bin\er_engine_diag.dll")) { throw 'er_engine_diag.dll was not built.' }
# The main release DLL must not contain diagnostic code: the F8 marker string exists only under ER_DIAG=1/2.
$dllText = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes("$out\bin\er_engine.dll"))
if ($dllText.Contains('===== ZNACZNIK')) { throw 'Release DLL contains diagnostic strings - was it built with /DER_DIAG=0?' }
# The tester DLL: log and F8 yes, the developer extras (.text dump of the game, A/B keys) no.
$diagText = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes("$out\bin\er_engine_diag.dll"))
if (-not $diagText.Contains('===== ZNACZNIK') -or -not $diagText.Contains('.prev.log')) { throw 'Tester DLL is not an ER_DIAG=2 build.' }
if ($diagText.Contains('text_dump_') -or $diagText.Contains('OMNIROLL: %s')) { throw 'Tester DLL contains developer diagnostics (.text dump / A/B keys).' }

# 2. DLL settings and game files (loaded by Mod Engine 2; the game folder is never touched).
Copy-Item "$dev\bin\er_engine.ini" "$out\bin\"
# [Update] is read only by setup\Update.ps1 (the DLL ignores it); add it if the dev ini does not have it.
$iniText = [IO.File]::ReadAllText("$out\bin\er_engine.ini")
# Sections with the DLL defaults, added when the dev ini lacks them so that users see the switches.
$iniSections = [ordered]@{
    'Fixes'  = "[Fixes]`r`n; 1 = after a roll the character is put back into free movement when it stands frozen with a direction held`r`n; 0 = off`r`nHangRepair=1"
    'Bosses' = "[Bosses]`r`n; Artorias phase 2 (needs files\chr\c4100.anibnd.dcx and files\script\m12_01_00_00.luabnd.dcx from this package)`r`n; 2 = automatic: on when those files are present, 1 = on, 0 = off (Artorias then dies at 0 HP, no phase 2)`r`nArtoriasPhase2=2`r`n; Gwyn phase 2 (in testing; needs files\chr\c5370.anibnd.dcx and files\script\m18_00_00_00.luabnd.dcx from this package)`r`n; 2 = automatic, 1 = on, 0 = off (Gwyn then dies at 0 HP; also remove those two files for the original Gwyn)`r`nGwynPhase2=2"
    'Update' = "[Update]`r`n; 1 = the launcher checks GitHub for a newer version of the mod before every start and asks before installing it`r`n; 0 = no check`r`nCheckForUpdates=1"
}
foreach ($s in $iniSections.Keys) {
    if ($iniText -notmatch "(?m)^\[$s\]") { $iniText = $iniText.TrimEnd() + "`r`n`r`n" + $iniSections[$s] + "`r`n" }
}
[IO.File]::WriteAllText("$out\bin\er_engine.ini", $iniText, $utf8NoBom)
Copy-Item "$dev\files\*" "$out\files\" -Recurse
if (-not (Test-Path "$out\files\chr\c0000.esd.dcx")) { throw 'files\chr\c0000.esd.dcx is missing in the dev mod folder.' }

# Boss GameParam: the shared one (main mod's GameParam with the ER lock-on camera + Artorias rows + Gwyn rows), built
# by tools\boss_gameparam.py; an older one would drop newer changes of the main GameParam. Its Artorias rows equal the
# released files_c4100_v2 ones (checked 2026-11-16: `boss_gameparam.py --artorias-tag _v2 --dry-run --check`).
$mainParam = Get-Item "$dev\files\param\GameParam\GameParam.parambnd.dcx"
$bossParam = Get-Item "$devBossParam\param\GameParam\GameParam.parambnd.dcx"
if ($bossParam.LastWriteTime -lt $mainParam.LastWriteTime) { throw 'Boss GameParam is older than the main one - rerun tools\boss_gameparam.py.' }
$rows = [IO.File]::ReadAllText("$devBossParam\boss_rows.txt")
if ($rows -notmatch '(?m)^artorias:' -or $rows -notmatch '(?m)^gwyn:') { throw 'Shared boss GameParam lacks the Artorias or Gwyn rows (boss_rows.txt).' }
New-Item -ItemType Directory -Force "$out\files\param\GameParam" | Out-Null
Copy-Item $bossParam.FullName "$out\files\param\GameParam\GameParam.parambnd.dcx" -Force
foreach ($f in $bossFiles) {
    if (-not (Test-Path "$devBoss\$f")) { throw "Boss file missing: $devBoss\$f" }
    New-Item -ItemType Directory -Force (Split-Path "$out\files\$f") | Out-Null
    Copy-Item "$devBoss\$f" "$out\files\$f" -Force
}
foreach ($f in $testBossFiles.Keys) {
    $src = Join-Path (Join-Path $root $testBossFiles[$f]) $f
    if (-not (Test-Path $src)) { throw "Test boss file missing: $src" }
    if (Test-Path "$out\files\$f") { throw "Test boss file would overwrite a mod file: files\$f" }
    New-Item -ItemType Directory -Force (Split-Path "$out\files\$f") | Out-Null
    Copy-Item $src "$out\files\$f" -Force
}
"DLL source: $DllSource"

# 3. Mod Engine 2 config. Paths are relative to the file, so it works wherever the folder is unpacked.
#    The setup tool writes the same file again together with the launcher .bat (which needs the ME2 path).
@"
# ER-Inspired DSR Remake v$Version - Mod Engine 2 configuration (Dark Souls Remastered).
# Paths are relative to this file. Run Setup.bat to create the launcher.
[modengine]
debug = false
external_dlls = [
    "bin/er_engine.dll",
]

[extension.mod_loader]
enabled = true
loose_params = false
mods = [
    { enabled = true, name = "er_inspired_dsr_remake", path = "files" },
]

[extension.scylla_hide]
enabled = false
"@ | ForEach-Object { [IO.File]::WriteAllText("$out\$fileBase.toml", $_.Replace("`r`n", "`n").Replace("`n", "`r`n"), $utf8NoBom) }
# Tester config (since 0.5.5): the same with the tester DLL. Static, so the updater brings it to older installs too.
$mainToml = [IO.File]::ReadAllText("$out\$fileBase.toml")
if (-not $mainToml.Contains('"bin/er_engine.dll"')) { throw 'Main toml has no bin/er_engine.dll entry.' }
$logsToml = $mainToml.Replace('"bin/er_engine.dll"', '"bin/er_engine_diag.dll"').Replace('Mod Engine 2 configuration', 'Mod Engine 2 configuration with the bug-report log (F8)')
[IO.File]::WriteAllText("$out\${fileBase}_logs.toml", $logsToml, $utf8NoBom)
# Its launcher reads the Mod Engine 2 folder remembered by Setup.bat (setup\modengine2_path.txt), so it needs no setup run.
@"
@echo off
chcp 65001 >nul
rem $fileBase - game start with the bug-report log (tester DLL bin\er_engine_diag.dll). Offline play only.
rem F8 in the game saves the log to bin\er_engine.log (the previous run is kept as bin\er_engine.prev.log).
cd /d "%~dp0"
set "MODENGINE2="
if exist "%~dp0setup\modengine2_path.txt" set /p MODENGINE2=<"%~dp0setup\modengine2_path.txt"
if not exist "%MODENGINE2%\modengine2_launcher.exe" (
    echo Najpierw uruchom Setup.bat i wskaz folder Mod Engine 2.
    echo Run Setup.bat first and choose the Mod Engine 2 folder.
    pause
    exit /b 1
)
echo Gra z logiem do zglaszania bledow: F8 w grze zapisuje bin\er_engine.log.
echo Game with the bug-report log: F8 in the game saves bin\er_engine.log.
"%MODENGINE2%\modengine2_launcher.exe" -t dsr -c "%~dp0${fileBase}_logs.toml"
"@ | Set-Content -Encoding ascii "$out\Launch_with_logs.bat"

# 4. Setup tool. Setup.ps1 is saved with a BOM: Windows PowerShell 5.1 reads BOM-less files as ANSI and
#    would break the Polish text in the window.
$ps1 = [IO.File]::ReadAllText("$PSScriptRoot\setup\Setup.ps1", [Text.Encoding]::UTF8)
$ps1 = $ps1.Replace('{VERSION}', $Version).Replace('{EXE_SHA256}', $exeSha256)
[IO.File]::WriteAllText("$out\setup\Setup.ps1", $ps1.Replace("`r`n", "`n").Replace("`n", "`r`n"), $utf8Bom)
$upd = [IO.File]::ReadAllText("$PSScriptRoot\setup\Update.ps1", [Text.Encoding]::UTF8)
$upd = $upd.Replace('{VERSION}', $Version).Replace('{REPO}', $Repo)
[IO.File]::WriteAllText("$out\setup\Update.ps1", $upd.Replace("`r`n", "`n").Replace("`n", "`r`n"), $utf8Bom)
# Linux setup (experimental): bash needs LF line endings and no BOM.
$sh = [IO.File]::ReadAllText("$PSScriptRoot\setup\Setup.sh", [Text.Encoding]::UTF8)
[IO.File]::WriteAllText("$out\setup\Setup.sh", $sh.Replace("`r`n", "`n"), $utf8NoBom)
@'
@echo off
chcp 65001 >nul
rem ER-Inspired DSR Remake - setup. Finds Mod Engine 2 and creates the launcher for the game. Installs nothing.
cd /d "%~dp0"
if not exist "%~dp0setup\Setup.ps1" (
    echo Najpierw rozpakuj cale archiwum do zwyklego folderu, a potem uruchom Setup.bat.
    echo Extract the whole archive to a normal folder first, then run Setup.bat.
    pause
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup\Setup.ps1" %*
if errorlevel 1 pause
'@ | Set-Content -Encoding ascii "$out\Setup.bat"

$readme = [IO.File]::ReadAllText("$PSScriptRoot\README_release.md", [Text.Encoding]::UTF8).Replace('{VERSION}', $Version)
[IO.File]::WriteAllText("$out\README.md", $readme, $utf8Bom)
$readmeEn = [IO.File]::ReadAllText("$PSScriptRoot\README_release_en.md", [Text.Encoding]::UTF8).Replace('{VERSION}', $Version)
[IO.File]::WriteAllText("$out\README_en.md", $readmeEn, $utf8Bom)
Copy-Item "$root\LICENSE" "$out\LICENSE.txt"

# 5. Archive (with the top-level folder inside, so extracting gives one folder).
$zip = Join-Path $root "dist\release\$name.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path $out -DestinationPath $zip
Get-ChildItem $out -Recurse -File | Select-Object @{n='File';e={$_.FullName.Substring($out.Length)}}, Length | Format-Table -AutoSize | Out-String -Width 160
"ZIP: $zip ($([int]((Get-Item $zip).Length/1KB)) KB)"

# 6. Setup tool test on a fresh copy extracted from the ZIP (the package itself stays clean).
if (-not $SkipInstallerTest) {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("er_remake_installer_test_" + [Guid]::NewGuid().ToString('N').Substring(0, 8))
    try {
        Expand-Archive -Path $zip -DestinationPath $tmp
        $pkg = Join-Path $tmp $name
        $inst = Join-Path $pkg 'setup\Setup.ps1'
        "--- setup tool test in $pkg"
        & powershell -NoProfile -ExecutionPolicy Bypass -File $inst -SelfTest -ModEngine2Path $devModEngine2
        if ($LASTEXITCODE -ne 0) { throw "Installer -SelfTest failed (exit $LASTEXITCODE)." }
        & powershell -NoProfile -ExecutionPolicy Bypass -File $inst -Silent -ModEngine2Path (Join-Path $tmp 'no_such_folder')
        if ($LASTEXITCODE -ne 1) { throw "Installer accepted a folder without Mod Engine 2 (exit $LASTEXITCODE)." }
        if (Test-Path $devModEngine2) {
            & powershell -NoProfile -ExecutionPolicy Bypass -File $inst -Silent -ModEngine2Path $devModEngine2
            if ($LASTEXITCODE -ne 0) { throw "Installer -Silent failed (exit $LASTEXITCODE)." }
            $bat = Join-Path $pkg "Launch_$fileBase.bat"
            if (-not (Test-Path $bat)) { throw 'Installer did not create the launcher .bat.' }
            if (-not ((Get-Content $bat -Raw).Contains("set `"MODENGINE2=$devModEngine2`""))) { throw 'Launcher .bat does not contain the Mod Engine 2 path.' }
            if (-not ((Get-Content $bat -Raw).Contains('setup\Update.ps1'))) { throw 'Launcher .bat does not run the update check.' }
            if (-not (Test-Path (Join-Path $pkg "$fileBase.toml"))) { throw 'Installer did not create the .toml.' }
            'Installer test: OK (window builds, wrong folder rejected, launcher and config generated)'

            # Updater: install the same package over this copy from the local zip (no network).
            $ini = Join-Path $pkg 'bin\er_engine.ini'
            [IO.File]::WriteAllText($ini, ([IO.File]::ReadAllText($ini) -replace '(?m)^OmniRoll=1', 'OmniRoll=0'))
            Set-Content -LiteralPath (Join-Path $pkg 'files\stale_file.txt') -Value 'x'
            $batBefore = Get-Content $bat -Raw
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $pkg 'setup\Update.ps1') -FromZip $zip -Yes
            if ($LASTEXITCODE -ne 0) { throw "Update.ps1 -FromZip failed (exit $LASTEXITCODE)." }
            if (-not ([IO.File]::ReadAllText($ini) -match '(?m)^OmniRoll=0')) { throw 'Updater did not keep the user value in er_engine.ini.' }
            if (-not ([IO.File]::ReadAllText($ini) -match '(?m)^CheckForUpdates=1')) { throw 'Updater lost the [Update] section of the new ini.' }
            if (Test-Path (Join-Path $pkg 'files\stale_file.txt')) { throw 'Updater did not remove a file that is not in the new package.' }
            if (-not (Test-Path (Join-Path $pkg "_backup\v$Version\files\stale_file.txt"))) { throw 'Updater did not back up the previous files.' }
            if ((Get-Content $bat -Raw) -ne $batBefore) { throw 'Updater changed the launcher .bat.' }
            if (-not (Test-Path (Join-Path $pkg 'bin\er_engine.dll'))) { throw 'DLL missing after the update.' }
            foreach ($f in 'bin\er_engine_diag.dll', "${fileBase}_logs.toml", 'Launch_with_logs.bat', 'setup\Setup.sh') {
                if (-not (Test-Path (Join-Path $pkg $f))) { throw "$f missing after the update." }
            }
            'Updater test: OK (local package installed, ini values kept, stale file removed, backup made, launcher untouched)'
        } else {
            "Installer test: Mod Engine 2 not found at $devModEngine2 - generation step skipped"
        }
    } finally {
        if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
    }
}
