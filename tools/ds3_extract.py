"""Extract chosen files from Dark Souls III's packed archives (Data#.bhd/.bdt) into work/ds3 (read only on the game).

The game folder is never written: each Data#.bhd header is RSA-decrypted in memory with the public keys shipped
with Nuxe (toolsy/Nuxe.1.2.1/.../BinderKeys/DarkSouls3_PC/Key), parsed by SoulsFormats BHD5, file names matched by
the 32-bit path hash against Nuxe's dictionaries (.../Hash/Data#.txt), and only the files asked for are read from
the .bdt (AES-encrypted ranges decrypted by SoulsFormats).

  python tools/ds3_extract.py c5280            # every dictionary path containing "c5280"
  python tools/ds3_extract.py /chr/c5280.anibnd.dcx /script/aicommon.luabnd.dcx
"""
from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sfbridge import load_soulsformats  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(r"F:\SteamLibrary\steamapps\common\DARK SOULS III\Game")
KEYS = Path(r"C:\Users\nemos\workspace\toolsy\Nuxe.1.2.1\Nuxe 1.2.1\res\BinderKeys\DarkSouls3_PC")
OUT = ROOT / "work" / "ds3"
ARCHIVES = ["Data1", "Data2", "Data3", "Data4", "Data5", "DLC1", "DLC2"]


def der_int(b: bytes, i: int) -> tuple[int, int]:
    assert b[i] == 0x02
    i += 1
    n = b[i]
    i += 1
    if n & 0x80:
        k = n & 0x7F
        n = int.from_bytes(b[i:i + k], "big")
        i += k
    return int.from_bytes(b[i:i + n], "big"), i + n


def rsa_key(pem: Path) -> tuple[int, int, int]:
    body = "".join(l for l in pem.read_text().splitlines() if not l.startswith("-----"))
    der = base64.b64decode(body)
    i = 1  # SEQUENCE
    i += 1 + (der[i] & 0x7F) if der[i] & 0x80 else 1
    n, i = der_int(der, i)
    e, _ = der_int(der, i)
    return n, e, (n.bit_length() + 7) // 8


def decrypt_header(path: Path, pem: Path) -> bytes:
    """Raw RSA with the public key, as UXM / Nuxe do: 256-byte blocks in, 255-byte blocks out (left-padded)."""
    n, e, size = rsa_key(pem)
    data = path.read_bytes()
    out = bytearray()
    for k in range(0, len(data), size):
        c = int.from_bytes(data[k:k + size], "big")
        out += pow(c, e, n).to_bytes(size - 1, "big")
    return bytes(out)


def path_hash(p: str) -> int:
    h = 0
    for ch in p.lower().replace("\\", "/"):
        h = (h * 37 + ord(ch)) & 0xFFFFFFFF
    return h


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("want", nargs="+", help="exact paths (start with /) or substrings of dictionary paths")
    ap.add_argument("--list", action="store_true", help="only list the matching paths")
    args = ap.parse_args(argv)
    sf = load_soulsformats()
    from System import Byte, Memory, Array
    from System.IO import File, FileMode, FileAccess, FileShare, FileStream
    done = 0
    for arc in ARCHIVES:
        dic = KEYS / "Hash" / f"{arc}.txt"
        if not dic.exists():
            continue
        names = [l.strip() for l in dic.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
        sel = [p for p in names if any((w == p) if w.startswith("/") else (w.lower() in p.lower()) for w in args.want)]
        if not sel:
            continue
        if args.list:
            for p in sel:
                print(f"{arc}: {p}")
            continue
        hdr = decrypt_header(GAME / f"{arc}.bhd", KEYS / "Key" / f"{arc}.pem")
        bhd = sf.BHD5.Read(Memory[Byte](Array[Byte](list(hdr))), sf.BHD5.Game.DarkSouls3)
        by_hash = {}
        for bucket in bhd.Buckets:
            for fh in bucket:
                by_hash[int(fh.FileNameHash)] = fh
        bdt = FileStream(str(GAME / f"{arc}.bdt"), FileMode.Open, FileAccess.Read, FileShare.Read)
        try:
            for p in sel:
                fh = by_hash.get(path_hash(p))
                if fh is None:
                    print(f"  {arc}: {p}: hash not in header")
                    continue
                raw = bytes(fh.ReadFile(bdt))
                size = int(fh.UnpaddedFileSize)
                if size > 0:
                    raw = raw[:size]
                dst = OUT / p.lstrip("/")
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(raw)
                done += 1
                print(f"  {arc}: {p} -> {dst.relative_to(ROOT)} ({len(raw)} B)")
        finally:
            bdt.Close()
    print(f"OK: {done} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
