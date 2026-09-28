"""BOAT RACE 公式「競走成績」テキスト（kYYMMDD.TXT, Shift_JIS）のパーサー。

ファイルは場ごとに ``NNKBGN`` 〜 ``NNKEND`` で区切られ、各レースは
``  1R  予選  H1800m ...`` という見出し行、出走表、払戻金の順で並ぶ。
固定桁ではなく正規表現で読むので、多少の桁ずれには耐えられる。
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from .models import Entry, Race

STADIUM_BEGIN = re.compile(r"^\s*(\d{2})KBGN")
STADIUM_END = re.compile(r"^\s*(\d{2})KEND")
RACE_HEADER = re.compile(r"^\s*(\d{1,2})R\s+(.*?)\s+H(\d{3,4})m")
# 着 艇 登番 選手名 ﾓｰﾀｰ ﾎﾞｰﾄ 展示 進入 ST ...  （選手名は全角スペース入り）
ENTRY_ROW = re.compile(
    r"^\s*(?P<status>\d{2}|[A-Z]\d?)\s+(?P<lane>[1-6])\s+(?P<racer>\d{4})\s+"
    r"(?P<name>[^ ]+(?: [^ \d][^ ]*)*?) +(?P<motor>\d{1,3})\s+(?P<boat>\d{1,3})"
    r"(?:\s+(?P<exhibit>\d\.\d{2}|\.))?(?:\s+(?P<course>[1-6]|\.))?"
    r"(?:\s+(?P<start>[FL]?\d?\.\d{2}|[FLK]\S*|\.))?"
)
DATE_IN_TEXT = re.compile(r"(20\d{2})\s*/\s*(\d{1,2})\s*/\s*(\d{1,2})")
DATE_IN_NAME = re.compile(r"[kK](\d{2})(\d{2})(\d{2})")
PAYOUT_PAIR = re.compile(r"(\d(?:-\d){0,2})\s+(\d+)")

BET_LABELS = [
    ("３連単", "trifecta"), ("3連単", "trifecta"),
    ("３連複", "trio"), ("3連複", "trio"),
    ("２連単", "exacta"), ("2連単", "exacta"),
    ("２連複", "quinella"), ("2連複", "quinella"),
    ("拡連複", "wide"), ("単勝", "win"), ("複勝", "place"),
]
COMBO_SIZE = {"win": 1, "place": 1, "exacta": 2, "quinella": 2, "wide": 2, "trifecta": 3, "trio": 3}


def _float(text: str | None) -> float | None:
    if not text or text == ".":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _start_timing(text: str | None) -> float | None:
    """スタートタイミング。"F.01" のようなフライングは負値にする。"""
    if not text or text == ".":
        return None
    sign = -1 if text.startswith("F") else 1
    value = _float(text.lstrip("FL"))
    return None if value is None else sign * value


def parse_entry(line: str) -> Entry | None:
    m = ENTRY_ROW.match(line)
    if not m:
        return None
    status = m["status"]
    course = m["course"]
    return Entry(
        lane=int(m["lane"]), racer_id=m["racer"],
        name=m["name"].replace("　", "").replace(" ", ""),
        motor=m["motor"], boat=m["boat"], exhibit=_float(m["exhibit"]),
        course=int(course) if course and course != "." else None,
        start=_start_timing(m["start"]),
        position=int(status) if status.isdigit() and 1 <= int(status) <= 6 else None,
        status=status,
    )


def _parse_payout_line(line: str, current: str | None) -> tuple[str | None, list[tuple[str, int]]]:
    """払戻金の行を読む。券種名が無い行は直前の券種の続き（複勝・拡連複の2行目以降）。"""
    text = unicodedata.normalize("NFKC", line)
    bet = None
    for label, name in BET_LABELS:
        label = unicodedata.normalize("NFKC", label)
        if label in text:
            bet = name
            text = text.split(label, 1)[1]
            break
    if bet is None:
        if current is None or not re.match(r"^\s+\d(?:-\d)*\s+\d+", text):
            return None, []
        bet = current
    if "特払" in text or "不成立" in text or "返還" in text:
        return bet, []
    size = COMBO_SIZE[bet]
    pairs = [(c, int(a)) for c, a in PAYOUT_PAIR.findall(text) if c.count("-") == size - 1]
    if size > 1:
        # "1-3  420  人気  1" の人気順位を拾わないよう、組番付きの最初のペアだけ採る
        pairs = pairs[:1]
    return bet, pairs


def parse_text(text: str, date: str | None = None) -> list[Race]:
    """競走成績テキスト 1 日分をパースしてレースのリストを返す。"""
    if date is None:
        m = DATE_IN_TEXT.search(text)
        if m:
            date = f"{m[1]}-{int(m[2]):02d}-{int(m[3]):02d}"
    if date is None:
        raise ValueError("日付が特定できません。date 引数で指定してください")

    races: dict[tuple[str, int], Race] = {}
    stadium: str | None = None
    race: Race | None = None
    bet: str | None = None

    for line in text.splitlines():
        if m := STADIUM_BEGIN.match(line):
            stadium, race, bet = m[1], None, None
            continue
        if STADIUM_END.match(line):
            stadium, race, bet = None, None, None
            continue
        if stadium is None:
            continue
        if m := RACE_HEADER.match(line):
            race = Race(date=date, stadium_code=stadium, race_no=int(m[1]),
                        race_name=re.sub(r"\s+", "", m[2]), distance=int(m[3]))
            bet = None
            # 場の冒頭にある払戻一覧などと重複しても、出走表を持つ方を採用する
            races.setdefault((stadium, race.race_no), race)
            if not races[(stadium, race.race_no)].entries:
                races[(stadium, race.race_no)] = race
            continue
        if race is None:
            continue
        if entry := parse_entry(line):
            race.entries.append(entry)
            continue
        new_bet, pairs = _parse_payout_line(line, bet)
        if new_bet:
            bet = new_bet
            race.payouts.setdefault(bet, []).extend(pairs)
        elif line.strip() and not line.strip().startswith(("-", "着")):
            bet = None

    return [r for r in races.values() if r.entries]


def date_from_filename(path: Path) -> str | None:
    m = DATE_IN_NAME.search(path.name)
    return f"20{m[1]}-{m[2]}-{m[3]}" if m else None


def parse_file(path: Path, encoding: str = "cp932") -> list[Race]:
    text = path.read_bytes().decode(encoding, errors="replace")
    return parse_text(text, date=date_from_filename(path))
