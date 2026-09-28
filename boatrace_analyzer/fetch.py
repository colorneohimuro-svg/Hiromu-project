"""BOAT RACE 公式サイトから競走成績（LZH 圧縮）をダウンロードして展開する。"""

from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

BASE_URL = "https://www1.mbrace.or.jp/od2/K/{ym}/k{ymd}.lzh"


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def extract_lzh(data: bytes, out_dir: Path) -> list[Path]:
    """LZH を展開する。lhafile パッケージ、無ければ lha / 7z コマンドを使う。"""
    try:
        import lhafile  # type: ignore
    except ImportError:
        lhafile = None
    if lhafile is not None:
        archive = lhafile.Lhafile(io.BytesIO(data))
        paths = []
        for info in archive.infolist():
            path = out_dir / Path(info.filename).name
            path.write_bytes(archive.read(info.filename))
            paths.append(path)
        return paths

    tool = shutil.which("lha") or shutil.which("7z")
    if tool is None:
        raise RuntimeError("LZH を展開できません。`pip install lhafile` するか lha / 7z を入れてください")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "data.lzh"
        src.write_bytes(data)
        if tool.endswith("lha"):
            cmd = [tool, "xqw=" + str(out_dir), str(src)]
        else:
            cmd = [tool, "x", "-y", f"-o{out_dir}", str(src)]
        subprocess.run(cmd, check=True, capture_output=True)
    return sorted(out_dir.glob("*.TXT")) + sorted(out_dir.glob("*.txt"))


def fetch_range(start: date, end: date, out_dir: Path, wait: float = 1.0, log=print) -> list[Path]:
    """期間内の競走成績を取得する。既に展開済みの日はスキップする。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for d in daterange(start, end):
        ymd = d.strftime("%y%m%d")
        existing = [p for p in out_dir.iterdir() if p.name.lower() == f"k{ymd}.txt"]
        if existing:
            saved.extend(existing)
            continue
        url = BASE_URL.format(ym=d.strftime("%Y%m"), ymd=ymd)
        try:
            with urllib.request.urlopen(url, timeout=30) as res:
                data = res.read()
        except urllib.error.HTTPError as e:
            log(f"{d}: 取得できませんでした (HTTP {e.code}) - 開催なしの可能性があります")
            continue
        except urllib.error.URLError as e:
            log(f"{d}: 接続エラー ({e.reason})")
            continue
        files = extract_lzh(data, out_dir)
        log(f"{d}: {', '.join(p.name for p in files)}")
        saved.extend(files)
        time.sleep(wait)  # 公式サーバーに負荷をかけないよう間隔を空ける
    return saved
