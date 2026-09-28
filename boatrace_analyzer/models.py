"""レース・出走・払戻のデータモデルと CSV 入出力。"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

STADIUMS = {
    "01": "桐生", "02": "戸田", "03": "江戸川", "04": "平和島", "05": "多摩川",
    "06": "浜名湖", "07": "蒲郡", "08": "常滑", "09": "津", "10": "三国",
    "11": "びわこ", "12": "住之江", "13": "尼崎", "14": "鳴門", "15": "丸亀",
    "16": "児島", "17": "宮島", "18": "徳山", "19": "下関", "20": "若松",
    "21": "芦屋", "22": "福岡", "23": "唐津", "24": "大村",
}

# 券種の内部名 -> (表示名, 組番の艇数, 順番を区別するか)
BET_TYPES = {
    "win": ("単勝", 1, True),
    "place": ("複勝", 1, True),
    "exacta": ("2連単", 2, True),
    "quinella": ("2連複", 2, False),
    "wide": ("拡連複", 2, False),
    "trifecta": ("3連単", 3, True),
    "trio": ("3連複", 3, False),
}


@dataclass
class Entry:
    lane: int                 # 艇番（枠番）
    racer_id: str
    name: str
    motor: str = ""
    boat: str = ""
    exhibit: float | None = None   # 展示タイム
    course: int | None = None      # 進入コース
    start: float | None = None     # スタートタイミング（フライングは負の値）
    position: int | None = None    # 着順（失格・欠場等は None）
    status: str = ""               # 着順欄の元の表記（"01", "F", "K0" など）


@dataclass
class Race:
    date: str                 # YYYY-MM-DD
    stadium_code: str
    race_no: int
    race_name: str = ""
    distance: int | None = None
    entries: list[Entry] = field(default_factory=list)
    # 券種 -> [(組番, 払戻金), ...]  同着時は複数
    payouts: dict[str, list[tuple[str, int]]] = field(default_factory=dict)

    @property
    def stadium(self) -> str:
        return STADIUMS.get(self.stadium_code, self.stadium_code)

    @property
    def key(self) -> tuple[str, str, int]:
        return (self.date, self.stadium_code, self.race_no)

    def finish_order(self) -> list[int]:
        """着順通りの艇番リスト（完走艇のみ）。"""
        finished = [e for e in self.entries if e.position is not None]
        return [e.lane for e in sorted(finished, key=lambda e: e.position)]

    def course_of(self, lane: int) -> int:
        for e in self.entries:
            if e.lane == lane:
                return e.course or lane
        return lane


RACE_FIELDS = ["date", "stadium_code", "stadium", "race_no", "race_name", "distance"] + list(BET_TYPES)
ENTRY_FIELDS = ["date", "stadium_code", "race_no", "lane", "course", "racer_id", "name",
                "motor", "boat", "exhibit", "start", "position", "status"]


def _fmt_payouts(items: list[tuple[str, int]]) -> str:
    return "|".join(f"{combo}:{amount}" for combo, amount in items)


def _parse_payouts(text: str) -> list[tuple[str, int]]:
    items = []
    for part in filter(None, text.split("|")):
        combo, amount = part.rsplit(":", 1)
        items.append((combo, int(amount)))
    return items


def _opt(value: str, conv):
    return conv(value) if value not in ("", None) else None


def save_csv(races: list[Race], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "races.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RACE_FIELDS)
        w.writeheader()
        for r in races:
            row = {"date": r.date, "stadium_code": r.stadium_code, "stadium": r.stadium,
                   "race_no": r.race_no, "race_name": r.race_name, "distance": r.distance or ""}
            for bt in BET_TYPES:
                row[bt] = _fmt_payouts(r.payouts.get(bt, []))
            w.writerow(row)
    with open(out_dir / "entries.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ENTRY_FIELDS)
        w.writeheader()
        for r in races:
            for e in r.entries:
                w.writerow({
                    "date": r.date, "stadium_code": r.stadium_code, "race_no": r.race_no,
                    "lane": e.lane, "course": e.course or "", "racer_id": e.racer_id,
                    "name": e.name, "motor": e.motor, "boat": e.boat,
                    "exhibit": "" if e.exhibit is None else e.exhibit,
                    "start": "" if e.start is None else e.start,
                    "position": e.position or "", "status": e.status,
                })


def load_csv(data_dir: Path) -> list[Race]:
    races: dict[tuple[str, str, int], Race] = {}
    with open(data_dir / "races.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            race = Race(date=row["date"], stadium_code=row["stadium_code"],
                        race_no=int(row["race_no"]), race_name=row["race_name"],
                        distance=_opt(row["distance"], int))
            for bt in BET_TYPES:
                if row.get(bt):
                    race.payouts[bt] = _parse_payouts(row[bt])
            races[race.key] = race
    entries_path = data_dir / "entries.csv"
    if entries_path.exists():
        with open(entries_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                race = races.get((row["date"], row["stadium_code"], int(row["race_no"])))
                if race is None:
                    continue
                race.entries.append(Entry(
                    lane=int(row["lane"]), racer_id=row["racer_id"], name=row["name"],
                    motor=row["motor"], boat=row["boat"],
                    exhibit=_opt(row["exhibit"], float), course=_opt(row["course"], int),
                    start=_opt(row["start"], float), position=_opt(row["position"], int),
                    status=row["status"],
                ))
    return list(races.values())
