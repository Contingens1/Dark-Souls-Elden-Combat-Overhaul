#!/usr/bin/env bash
# ER-Inspired DSR Remake - Linux setup (Steam + Proton). Counterpart of Setup.ps1 / Setup.bat.
# Installs nothing. It locates Steam, Dark Souls Remastered (appid 570940) and Mod Engine 2, writes the Mod Engine 2
# configs (.toml) and a launch script into the mod folder, and PRINTS what you must do next (Polish, then English).
#
# It never writes into the game folder, the Proton prefix or Steam's own config - only inside this package folder.
# Needs only bash + coreutils + grep/sed/awk/find. No sudo.
#
# Usage:  bash setup/Setup.sh [--me2 DIR] [--steam DIR] [--help]
#   --me2 DIR    folder with modengine2_launcher.exe (a Mod Engine 2 build with Dark Souls Remastered support)
#   --steam DIR  Steam root to use instead of auto-detection
#
# Exit codes: 0 ok, 1 error (package / Mod Engine 2 not found), 2 ok but Mod Engine 2 has no Dark Souls Remastered support.
set -euo pipefail

FILE_BASE='ER-Inspired_DSR_Remake'
MOD_NAME='ER-Inspired DSR Remake'
LAUNCHER_EXE='modengine2_launcher.exe'
APPID=570940

SELF="${BASH_SOURCE[0]}"
SETUP_DIR="$(cd "$(dirname "$SELF")" && pwd)"
PKG_DIR="$(cd "$SETUP_DIR/.." && pwd)"
TOML_MAIN="$PKG_DIR/$FILE_BASE.toml"
TOML_LOGS="$PKG_DIR/${FILE_BASE}_logs.toml"
LAUNCH_SH="$PKG_DIR/Launch_$FILE_BASE.sh"
REMEMBER="$SETUP_DIR/modengine2_path_linux.txt"

ME2_ARG=''
STEAM_ARG=''
while [ $# -gt 0 ]; do
    case "$1" in
        --me2)   [ $# -ge 2 ] || { echo "Brak wartosci dla --me2 / missing value for --me2"; exit 1; }; ME2_ARG="$2"; shift 2 ;;
        --steam) [ $# -ge 2 ] || { echo "Brak wartosci dla --steam / missing value for --steam"; exit 1; }; STEAM_ARG="$2"; shift 2 ;;
        -h|--help) sed -n '2,13p' "$SELF" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "Nieznana opcja / unknown option: $1 (try --help)"; exit 1 ;;
    esac
done

HOME_DIR="${HOME:-}"
[ -n "$HOME_DIR" ] || { echo "HOME nie jest ustawiony / HOME is not set"; exit 1; }

say() { printf '%s\n' "$*"; }
warn() { printf 'UWAGA / WARNING: %s\n' "$*"; }

# --- Package check -----------------------------------------------------------------------------------
version=''
case "$(basename "$PKG_DIR")" in
    *_v[0-9]*) version="${PKG_DIR##*_v}" ;;
esac
missing=()
for rel in bin/er_engine.dll bin/er_engine.ini files; do
    [ -e "$PKG_DIR/$rel" ] || missing+=("$rel")
done
if [ ${#missing[@]} -gt 0 ]; then
    say "BLAD: w folderze moda brakuje: ${missing[*]}. Rozpakuj cale archiwum jeszcze raz."
    say "ERROR: missing in the mod folder: ${missing[*]}. Unpack the whole archive again."
    exit 1
fi
if [ -e "$PKG_DIR/DarkSoulsRemastered.exe" ]; then
    say "BLAD: mod jest rozpakowany w katalogu gry. Przenies folder moda gdzie indziej (np. ~/Games) i uruchom ponownie."
    say "ERROR: the mod is unpacked inside the game folder. Move it elsewhere (e.g. ~/Games) and run this again."
    exit 1
fi
HAVE_DIAG=0
[ -f "$PKG_DIR/bin/er_engine_diag.dll" ] && HAVE_DIAG=1

# --- Helpers -----------------------------------------------------------------------------------------
real() { readlink -f -- "$1" 2>/dev/null || printf '%s' "$1"; }

# Prints the values of all "path" keys in a Steam libraryfolders.vdf (backslashes un-escaped).
vdf_paths() {
    [ -f "$1" ] || return 0
    sed -n 's/^[[:space:]]*"path"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$1" | sed 's/\\\\/\\/g'
}

# Value of a quoted key in an .acf / .vdf file.
vdf_value() {
    [ -f "$2" ] || return 0
    sed -n 's/^[[:space:]]*"'"$1"'"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$2" | head -n 1
}

# --- Mod Engine 2 validation (same rules as Test-ModEngine2) ------------------------------------------
# Sets ME2_PATH (normalized folder), ME2_DSR (1/0). Returns 1 when there is no launcher in the folder.
test_me2() {
    local dir="$1"
    ME2_PATH=''; ME2_DSR=0
    dir="${dir#"${dir%%[![:space:]]*}"}"; dir="${dir%"${dir##*[![:space:]]}"}"   # trim
    dir="${dir#\"}"; dir="${dir%\"}"
    case "$dir" in "~") dir="$HOME_DIR" ;; "~/"*) dir="$HOME_DIR/${dir#\~/}" ;; esac
    case "$dir" in */"$LAUNCHER_EXE") dir="$(dirname "$dir")" ;; esac    # the user gave the exe itself
    [ -n "$dir" ] && [ -d "$dir" ] || return 1
    dir="$(real "$dir")"
    [ -f "$dir/$LAUNCHER_EXE" ] || return 1
    ME2_PATH="$dir"
    if [ -f "$dir/launchmod_darksoulsremastered.bat" ] || [ -f "$dir/config_darksoulsremastered.toml" ]; then
        ME2_DSR=1
    elif LC_ALL=C grep -aqi 'darksoulsremastered' "$dir/$LAUNCHER_EXE" 2>/dev/null ||
         LC_ALL=C grep -aqi 'd.a.r.k.s.o.u.l.s.r.e.m.a.s.t.e.r.e.d' "$dir/$LAUNCHER_EXE" 2>/dev/null; then
        ME2_DSR=1
    fi
    return 0
}

# --- Mod Engine 2 search (same order as Find-ModEngine2: remembered, near the mod, user folders) -------
ME2_FOUND=()
add_me2() {
    local d
    test_me2 "$1" || return 0
    for d in ${ME2_FOUND[@]+"${ME2_FOUND[@]}"}; do [ "$d" = "$ME2_PATH" ] && return 0; done
    ME2_FOUND+=("$ME2_PATH")
}
search_me2_in() {   # dir maxdepth
    [ -d "$1" ] || return 0
    local f
    while IFS= read -r f; do
        [ -n "$f" ] && add_me2 "$(dirname "$f")"
    done < <(find "$1" -maxdepth "$2" -type f -iname "$LAUNCHER_EXE" 2>/dev/null || true)
}
find_me2() {
    ME2_FOUND=()
    if [ -f "$REMEMBER" ]; then
        add_me2 "$(head -n 1 "$REMEMBER" 2>/dev/null || true)"
    fi
    local p="$PKG_DIR" i
    for i in 1 2 3; do search_me2_in "$p" 3; p="$(dirname "$p")"; [ "$p" = "/" ] && break; done
    local d
    for d in Downloads Games Desktop Documents Applications ModEngine2 modengine2 .local/share; do
        search_me2_in "$HOME_DIR/$d" 4
    done
    # the rest of the home folder, shallow, skipping hidden folders (Steam, caches, Wine prefixes live there)
    local f
    while IFS= read -r f; do
        [ -n "$f" ] && add_me2 "$(dirname "$f")"
    done < <(find "$HOME_DIR" -maxdepth 3 \( -name '.*' -prune \) -o -type f -iname "$LAUNCHER_EXE" -print 2>/dev/null || true)
    # SD card / external drives (Steam Deck: /run/media/...)
    for d in /run/media /media /mnt; do search_me2_in "$d" 4; done
    # builds with Dark Souls Remastered support first (stable order otherwise)
    local with=() without=() x
    for x in ${ME2_FOUND[@]+"${ME2_FOUND[@]}"}; do
        test_me2 "$x" || continue
        if [ "$ME2_DSR" = 1 ]; then with+=("$x"); else without+=("$x"); fi
    done
    ME2_FOUND=(${with[@]+"${with[@]}"} ${without[@]+"${without[@]}"})
}

# --- Steam / game / Proton prefix (read only) --------------------------------------------------------
STEAM_ROOT=''; STEAM_FLATPAK=0
GAME_LIB=''; GAME_EXE=''; GAME_PFX=''
find_steam() {
    local c r
    local cands=()
    [ -n "$STEAM_ARG" ] && cands+=("$STEAM_ARG")
    cands+=("$HOME_DIR/.steam/steam" "$HOME_DIR/.local/share/Steam" "$HOME_DIR/.var/app/com.valvesoftware.Steam/.local/share/Steam" "$HOME_DIR/.steam/root")
    for c in "${cands[@]}"; do
        [ -d "$c/steamapps" ] || continue
        r="$(real "$c")"
        STEAM_ROOT="$r"
        case "$r" in *com.valvesoftware.Steam*) STEAM_FLATPAK=1 ;; esac
        return 0
    done
    return 1
}
find_game() {
    local libs=() seen=() lib l dup root_real vdf inst
    root_real="$STEAM_ROOT"
    libs+=("$root_real")
    for vdf in "$root_real/steamapps/libraryfolders.vdf" "$root_real/config/libraryfolders.vdf"; do
        while IFS= read -r l; do [ -n "$l" ] && libs+=("$l"); done < <(vdf_paths "$vdf")
    done
    for lib in "${libs[@]}"; do
        [ -d "$lib" ] || continue
        lib="$(real "$lib")"
        dup=0
        for l in ${seen[@]+"${seen[@]}"}; do [ "$l" = "$lib" ] && dup=1; done
        [ "$dup" = 1 ] && continue
        seen+=("$lib")
        inst=''
        if [ -f "$lib/steamapps/appmanifest_$APPID.acf" ]; then
            inst="$(vdf_value installdir "$lib/steamapps/appmanifest_$APPID.acf")"
        fi
        [ -n "$inst" ] || inst='DARK SOULS REMASTERED'
        if [ -f "$lib/steamapps/common/$inst/DarkSoulsRemastered.exe" ]; then
            GAME_LIB="$lib"
            GAME_EXE="$lib/steamapps/common/$inst/DarkSoulsRemastered.exe"
            [ -d "$lib/steamapps/compatdata/$APPID/pfx" ] && GAME_PFX="$lib/steamapps/compatdata/$APPID/pfx"
            return 0
        fi
    done
    return 1
}

# --- Writing the mod files ---------------------------------------------------------------------------
write_toml() {   # file dll-relative-path
    local ver=''
    [ -n "$version" ] && ver=" v$version"
    cat > "$1" <<EOF
# $MOD_NAME$ver - Mod Engine 2 configuration (Dark Souls Remastered).
# Generated by Setup.sh. Paths are relative to this file.
[modengine]
debug = false
external_dlls = [
    "$2",
]

[extension.mod_loader]
enabled = true
loose_params = false
mods = [
    { enabled = true, name = "er_inspired_dsr_remake", path = "files" },
]

[extension.scylla_hide]
enabled = false
EOF
}

sq() { local s=$1; printf "'%s'" "${s//\'/\'\\\'\'}"; }   # single-quote a string for a shell script

write_launch_script() {   # me2dir
    {
        printf '%s\n' '#!/usr/bin/env bash'
        printf '# %s - launch script generated by Setup.sh. Do not edit; run setup/Setup.sh again instead.\n' "$MOD_NAME"
        printf 'ME2_DIR=%s\n' "$(sq "$1")"
        printf 'PKG_DIR=%s\n' "$(sq "$PKG_DIR")"
        printf 'FILE_BASE=%s\n' "$(sq "$FILE_BASE")"
        printf 'APPID=%s\n' "$APPID"
        cat <<'LAUNCH_EOF'
#
# HOW IT WORKS (design notes)
# Set the game's Steam launch options to:   "<this script>" %command%
# Steam then runs this script with the complete Proton command line, for example
#   reaper SteamLaunch AppId=570940 -- <runtime>/_v2-entry-point --verb=waitforexitandrun -- <proton>/proton waitforexitandrun
#       "<library>/steamapps/common/DARK SOULS REMASTERED/DarkSoulsRemastered.exe"
# (with or without the SteamLinuxRuntime wrapper). We find the argument that is DarkSoulsRemastered.exe and replace
# it with modengine2_launcher.exe plus "-t dsr -c <toml>" (Wine path Z:\...). Everything before it (Steam reaper,
# the container, proton itself) is kept, so Mod Engine 2 runs inside the game's own Proton prefix and with Steam's
# environment, and then starts the game and injects its DLLs. This is the same mechanism Seamless Co-op uses on Linux.
#
# Why the game exe is also passed with -p (default): inside Proton the launcher cannot find the game through the
# registry / Steam library lookup (the prefix only has Proton's stub Steam), and upstream Mod Engine 2 has
# "-p/--game-path". The path is given as a Wine path (Z:\ + the Linux path). If your Mod Engine 2 build refuses it
# (upstream derives the install dir with parent().parent(), which suits "Game/xxx.exe" layouts), use --no-game-path.
#
# __COMPAT_LAYER=RunAsInvoker: reports exist of "Couldn't create process: 2e4" (0x2E4 = ERROR_ELEVATION_REQUIRED)
# when launching DSR through the Mod Engine 2 launcher under Wine. RunAsInvoker tells Wine not to demand elevation.
# It is harmless otherwise. Disable with ER_NO_RUNASINVOKER=1.
#
# Fallback if the Steam launch option route does not work (may hit the same 2e4 error):
#   protontricks-launch --appid 570940 "$ME2_DIR/modengine2_launcher.exe" -t dsr -c "<toml>"
#
# Options (put them before %command%):  --logs  use the _logs config (er_engine_diag.dll, F8 saves bin/er_engine.log)
#   --dry-run  only print the rewritten command   --no-game-path  do not pass -p   --help
set -u

LOGS=0; DRY=0; GAMEPATH=1
while [ $# -gt 0 ]; do
    case "$1" in
        --logs) LOGS=1; shift ;;
        --dry-run) DRY=1; shift ;;
        --no-game-path) GAMEPATH=0; shift ;;
        -h|--help) sed -n '/^# Options/,/^set -u/p' "$0" | sed '$d;s/^# \{0,1\}//'; exit 0 ;;
        --) shift; break ;;
        *) break ;;
    esac
done

usage() {
    cat <<EOF
Ten skrypt nie dostal polecenia Steama. Uruchamiaj go z Steama: Wlasciwosci gry -> Opcje uruchamiania:
    "$PKG_DIR/Launch_$FILE_BASE.sh" %command%
(wariant z logami:  "$PKG_DIR/Launch_$FILE_BASE.sh" --logs %command% )

This script got no Steam command line. Start it from Steam: game Properties -> Launch Options:
    "$PKG_DIR/Launch_$FILE_BASE.sh" %command%
(logs variant:      "$PKG_DIR/Launch_$FILE_BASE.sh" --logs %command% )
EOF
    if command -v protontricks-launch >/dev/null 2>&1; then
        cat <<EOF

protontricks wykryty / protontricks found - alternatywa / alternative (moze dac blad 2e4 / may fail with 2e4):
    protontricks-launch --appid $APPID "$ME2_DIR/modengine2_launcher.exe" -t dsr -c "Z:$(printf '%s' "$PKG_DIR/$FILE_BASE.toml" | tr / '\\')"
EOF
    fi
}

if [ $# -eq 0 ]; then usage; exit 2; fi

# Prefer the folder this script sits in (the mod folder may have been moved after Setup.sh).
here="$(cd "$(dirname "$0")" 2>/dev/null && pwd || true)"
if [ -n "$here" ] && [ -f "$here/$FILE_BASE.toml" ]; then PKG_DIR="$here"; fi

TOML="$PKG_DIR/$FILE_BASE.toml"
if [ "$LOGS" = 1 ]; then TOML="$PKG_DIR/${FILE_BASE}_logs.toml"; fi

to_win() { case "$1" in /*) printf 'Z:%s' "$(printf '%s' "$1" | tr / '\\')" ;; *) printf '%s' "$1" ;; esac; }

run_original() {
    local msg="$1"; shift
    echo "[Launch_$FILE_BASE] UWAGA/WARNING: $msg" >&2
    echo "[Launch_$FILE_BASE] Gra uruchomi sie BEZ moda / the game will start WITHOUT the mod." >&2
    if [ "$DRY" = 1 ]; then printf 'ORIGINAL COMMAND:'; printf ' %q' "$@"; echo; exit 0; fi
    exec "$@"
}
orig=("$@")
shift 0

idx=-1; i=0
for a in "${orig[@]}"; do
    base="${a##*[/\\]}"
    if [ "${base,,}" = "darksoulsremastered.exe" ]; then idx=$i; break; fi
    i=$((i+1))
done
if [ "$idx" -lt 0 ]; then
    run_original "w poleceniu Steama nie ma DarkSoulsRemastered.exe / no DarkSoulsRemastered.exe in the Steam command" "${orig[@]}"
fi
[ -f "$ME2_DIR/modengine2_launcher.exe" ] || run_original "brak $ME2_DIR/modengine2_launcher.exe - uruchom ponownie Setup.sh / Mod Engine 2 missing, run Setup.sh again" "${orig[@]}"
[ -f "$TOML" ] || run_original "brak $TOML - uruchom ponownie Setup.sh / config missing, run Setup.sh again (the _logs config needs bin/er_engine_diag.dll in the package)" "${orig[@]}"

gameexe="${orig[$idx]}"
new=("${orig[@]:0:$idx}" "$ME2_DIR/modengine2_launcher.exe" -t dsr -c "$(to_win "$TOML")")
if [ "$GAMEPATH" = 1 ]; then new+=(-p "$(to_win "$gameexe")"); fi
rest=$(( ${#orig[@]} - idx - 1 ))
if [ "$rest" -gt 0 ]; then
    echo "[Launch_$FILE_BASE] pominieto $rest dodatkowych argumentow po exe gry / dropped $rest extra argument(s) after the game exe" >&2
fi

if [ -z "${ER_NO_RUNASINVOKER:-}" ]; then export __COMPAT_LAYER=RunAsInvoker; fi

if [ "$DRY" = 1 ]; then
    echo "REWRITTEN COMMAND (one argument per line):"
    for a in "${new[@]}"; do printf '  %q\n' "$a"; done
    [ "$LOGS" = 1 ] && echo "(logs variant: $TOML)"
    exit 0
fi
echo "[Launch_$FILE_BASE] $(basename "$TOML") -> Mod Engine 2 w prefiksie gry / inside the game's Proton prefix" >&2
exec "${new[@]}"
LAUNCH_EOF
    } > "$LAUNCH_SH"
    chmod +x "$LAUNCH_SH"
}

# --- Run ---------------------------------------------------------------------------------------------
say "== $MOD_NAME${version:+ v$version} - konfiguracja Linux / Linux setup =="

# Mod Engine 2
ME2_DIR=''; ME2_HAS_DSR=0
if [ -n "$ME2_ARG" ]; then
    if test_me2 "$ME2_ARG"; then ME2_DIR="$ME2_PATH"; ME2_HAS_DSR="$ME2_DSR"
    else
        say "BLAD: w '$ME2_ARG' nie ma pliku $LAUNCHER_EXE. Wskaz folder, w ktorym lezy ten plik."
        say "ERROR: no $LAUNCHER_EXE in '$ME2_ARG'. Point --me2 at the folder that contains it."
        exit 1
    fi
else
    find_me2
    if [ ${#ME2_FOUND[@]} -gt 0 ]; then
        test_me2 "${ME2_FOUND[0]}" || true
        ME2_DIR="$ME2_PATH"; ME2_HAS_DSR="$ME2_DSR"
        if [ ${#ME2_FOUND[@]} -gt 1 ]; then
            say "Znaleziono ${#ME2_FOUND[@]} kopie Mod Engine 2 (uzywam pierwszej; inna: --me2 DIR) / found ${#ME2_FOUND[@]} copies (using the first; other: --me2 DIR):"
            printf '  %s\n' "${ME2_FOUND[@]}"
        fi
    fi
fi
if [ -z "$ME2_DIR" ]; then
    cat <<EOF
BLAD: nie znaleziono Mod Engine 2 (plik $LAUNCHER_EXE).
  Pobierz Mod Engine 2 z wersja obslugujaca Dark Souls Remastered (https://github.com/soulsmods/ModEngine2 -
  zob. README moda, sekcja Wymagania), rozpakuj go gdziekolwiek (np. ~/Games/ModEngine2) i uruchom:
      bash "$SETUP_DIR/Setup.sh" --me2 "/sciezka/do/ModEngine2"
ERROR: Mod Engine 2 ($LAUNCHER_EXE) was not found.
  Download a Mod Engine 2 build with Dark Souls Remastered support (https://github.com/soulsmods/ModEngine2 -
  see the mod README, Requirements), unpack it anywhere (e.g. ~/Games/ModEngine2) and run:
      bash "$SETUP_DIR/Setup.sh" --me2 "/path/to/ModEngine2"
EOF
    exit 1
fi
if [ "$ME2_HAS_DSR" = 1 ]; then
    say "Mod Engine 2 z obsluga Dark Souls Remastered: $ME2_DIR"
    say "Mod Engine 2 with Dark Souls Remastered support: $ME2_DIR"
else
    warn "Znaleziono Mod Engine 2 ($ME2_DIR), ale wyglada na wydanie BEZ obslugi Dark Souls Remastered (brak config_darksoulsremastered.toml). Mod najpewniej sie nie uruchomi."
    warn "Mod Engine 2 found ($ME2_DIR) but it looks like a build WITHOUT Dark Souls Remastered support. The mod will most likely not start."
fi

# Files (inside the mod folder only)
write_toml "$TOML_MAIN" "bin/er_engine.dll"
say "Zapisano / written: $TOML_MAIN"
if [ "$HAVE_DIAG" = 1 ]; then
    write_toml "$TOML_LOGS" "bin/er_engine_diag.dll"
    say "Zapisano / written: $TOML_LOGS"
else
    rm -f "$TOML_LOGS"
    say "Brak bin/er_engine_diag.dll w tej paczce - pominieto wariant z logami / no bin/er_engine_diag.dll in this package - logs variant skipped."
fi
write_launch_script "$ME2_DIR"
printf '%s' "$ME2_DIR" > "$REMEMBER"
say "Zapisano / written: $LAUNCH_SH"

# Steam / game / prefix (information only)
STEAM_OK=0; GAME_OK=0
if find_steam; then
    STEAM_OK=1
    say "Steam: $STEAM_ROOT"
    if [ "$STEAM_FLATPAK" = 1 ]; then
        warn "Steam z Flatpaka: Steam widzi tylko wybrane foldery. Folder moda i Mod Engine 2 musza byc dla niego dostepne, np.:  flatpak override --user --filesystem=\"$PKG_DIR\" --filesystem=\"$ME2_DIR\" com.valvesoftware.Steam"
        warn "Flatpak Steam sees only selected folders. The mod folder and Mod Engine 2 must be reachable, e.g. the override command above."
    fi
    if find_game; then
        GAME_OK=1
        say "Dark Souls Remastered: $GAME_EXE"
        if [ -n "$GAME_PFX" ]; then
            say "Prefiks Proton / Proton prefix: $GAME_PFX"
        else
            warn "Nie ma jeszcze prefiksu Proton (steamapps/compatdata/$APPID/pfx) - gra nigdy nie byla uruchomiona przez Proton. Wlacz Proton dla gry (Wlasciwosci -> Zgodnosc -> Wymus uzycie narzedzia, np. Proton Experimental / 9.x), uruchom ja raz do menu glownego, zamknij i wtedy uzyj trybu z modem."
            warn "No Proton prefix yet (steamapps/compatdata/$APPID/pfx): the game has never run under Proton. Force a Proton version for it (Properties -> Compatibility), start it once to the main menu, quit, then use the modded launch."
        fi
    else
        warn "Nie znaleziono Dark Souls Remastered (appid $APPID) w bibliotekach Steama (libraryfolders.vdf). Zainstaluj grę lub sprawdz biblioteke. Pliki moda i tak zostaly zapisane."
        warn "Dark Souls Remastered (appid $APPID) was not found in the Steam libraries. Install it or check the library. The mod files were written anyway."
    fi
else
    warn "Nie znaleziono Steama (~/.steam/steam, ~/.local/share/Steam, Flatpak). Mozesz podac: --steam /sciezka/do/Steam. Pliki moda i tak zostaly zapisane."
    warn "Steam not found (~/.steam/steam, ~/.local/share/Steam, Flatpak). You can pass --steam /path/to/Steam. The mod files were written anyway."
fi

LINE="\"$LAUNCH_SH\" %command%"
LINE_LOGS="\"$LAUNCH_SH\" --logs %command%"
PT_TOML="Z:$(printf '%s' "$TOML_MAIN" | tr / '\\')"

cat <<EOF

================ CO DALEJ (PL) ================
1. W Steam: prawy klik na Dark Souls Remastered -> Wlasciwosci -> Ogolne -> Opcje uruchamiania. Wklej DOKLADNIE:
       $LINE
2. Wlasciwosci -> Zgodnosc: wymus Proton (np. Proton Experimental albo 9.x). Gra musi byc raz uruchomiona pod Protonem
   (musi istniec prefiks), potem uruchamiaj ja zwykle przyciskiem Graj w Steam - z modem. Graj wylacznie offline.
3. Sprawdzenie w grze: po zablokowaniu celu (lock-on) unik/turlanie dziala w 360 stopni (styl Elden Ring).
4. Zglaszanie bledow (wariant z logami):
       $LINE_LOGS
   Po tej zmianie F8 w grze zapisuje log do bin/er_engine.log w folderze moda (zwykly wariant nie tworzy logu).
   Wrocisz do zwyklego wariantu przywracajac linie z punktu 1. (wariant z logami istnieje tylko w paczkach z bin/er_engine_diag.dll).
5. Test bez gry: w terminalu uruchom (z dowolnym poleceniem podobnym do Steama):
       "$LAUNCH_SH" --dry-run <polecenie jak od Steama>
6. Jesli to nie dziala: pokaz mi wynik w terminalu (uruchom Steam z terminala: steam) oraz plik bin/er_engine.log (wariant z logami).
   Awaryjnie, tylko gdy masz protontricks (czesto konczy sie bledem 2e4):
       protontricks-launch --appid $APPID "$ME2_DIR/$LAUNCHER_EXE" -t dsr -c "$PT_TOML"
   Skrypt niczego nie zapisuje w folderze gry, prefiksie ani konfiguracji Steama.

================ NEXT STEPS (EN) ==============
1. In Steam: right-click Dark Souls Remastered -> Properties -> General -> Launch Options. Paste EXACTLY:
       $LINE
2. Properties -> Compatibility: force a Proton version (e.g. Proton Experimental or 9.x). The game must have been started once
   under Proton (the prefix must exist); after that launch it normally with Play in Steam - it starts with the mod.
   Play offline only.
3. In-game check: while locked on, the dodge/roll works in 360 degrees (Elden Ring style).
4. Bug reports (logs variant):
       $LINE_LOGS
   With this line, F8 in game saves the log to bin/er_engine.log in the mod folder (the normal variant writes no log).
   Switch back by restoring the line from step 1 (the logs variant exists only in packages that contain bin/er_engine_diag.dll).
5. Test without the game: run "$LAUNCH_SH" --dry-run <a Steam-like command> in a terminal.
6. If it does not work: send me the terminal output (start Steam from a terminal: steam) and bin/er_engine.log (logs variant).
   Fallback, only if protontricks is installed (often fails with error 2e4):
       protontricks-launch --appid $APPID "$ME2_DIR/$LAUNCHER_EXE" -t dsr -c "$PT_TOML"
   This script never writes into the game folder, the Proton prefix or Steam's configuration.
EOF

[ "$ME2_HAS_DSR" = 1 ] || exit 2
exit 0
