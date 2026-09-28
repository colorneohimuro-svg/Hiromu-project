"""集計・バックテスト。"""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from dataclasses import dataclass

from .models import BET_TYPES, STADIUMS, Race

BET_ALIASES = {
    "win": "win", "単勝": "win", "1t": "win",
    "exacta": "exacta", "2t": "exacta", "2連単": "exacta",
    "quinella": "quinella", "2f": "quinella", "2連複": "quinella",
    "trifecta": "trifecta", "3t": "trifecta", "3連単": "trifecta",
    "trio": "trio", "3f": "trio", "3連複": "trio",
}


def filter_races(races: list[Race], stadium: str | None = None,
                 date_from: str | None = None, date_to: str | None = None) -> list[Race]:
    code = None
    if stadium:
        code = stadium if stadium in STADIUMS else next(
            (c for c, n in STADIUMS.items() if n == stadium), None)
        if code is None:
            raise ValueError(f"不明な場です: {stadium}")
    return [
        r for r in races
        if (code is None or r.stadium_code == code)
        and (date_from is None or r.date >= date_from)
        and (date_to is None or r.date <= date_to)
    ]


# ---------------------------------------------------------------- コース別成績

@dataclass
class CourseStat:
    course: int
    starts: int = 0
    first: int = 0
    top2: int = 0
    top3: int = 0
    st_sum: float = 0.0
    st_count: int = 0

    def rate(self, n: int) -> float:
        return n / self.starts if self.starts else 0.0

    @property
    def avg_st(self) -> float | None:
        return self.st_sum / self.st_count if self.st_count else None


def course_stats(races: list[Race]) -> list[CourseStat]:
    stats = {c: CourseStat(c) for c in range(1, 7)}
    for race in races:
        for e in race.entries:
            course = e.course or e.lane
            if course not in stats or e.status.startswith("K"):  # 欠場は除外
                continue
            s = stats[course]
            s.starts += 1
            if e.position:
                s.first += e.position == 1
                s.top2 += e.position <= 2
                s.top3 += e.position <= 3
            if e.start is not None and e.start >= 0:
                s.st_sum += e.start
                s.st_count += 1
    return [stats[c] for c in range(1, 7)]


# ---------------------------------------------------------------- 出目ランキング

@dataclass
class ComboStat:
    combo: str
    hits: int
    total_payout: int

    @property
    def avg_payout(self) -> float:
        return self.total_payout / self.hits if self.hits else 0.0


def combo_ranking(races: list[Race], bet_type: str = "trifecta") -> tuple[int, list[ComboStat]]:
    """券種ごとの出目の出現回数と平均配当。戻り値は (対象レース数, ランキング)。"""
    counts: Counter[str] = Counter()
    payouts: Counter[str] = Counter()
    n = 0
    for race in races:
        items = race.payouts.get(bet_type)
        if not items:
            continue
        n += 1
        for combo, amount in items:
            counts[combo] += 1
            payouts[combo] += amount
    ranking = [ComboStat(c, k, payouts[c]) for c, k in counts.most_common()]
    return n, ranking


# ---------------------------------------------------------------- 買い目・バックテスト

def parse_bet(spec: str) -> tuple[str, list[str]]:
    """買い目の指定を展開する。

    書式は ``券種:フォーメーション``。各着の候補艇を ``-`` で区切って並べる。
      3t:1-2-3      3連単 1-2-3 の 1 点
      3t:1-23-234   3連単 1着1, 2着2か3, 3着2か3か4 （4 点）
      3f:1-2-34     3連複 （順不同。重複は除く）
      2t:1-all      2連単 1 着固定の流し （all は 1〜6 全艇）
      win:1         単勝 1
    """
    if ":" not in spec:
        raise ValueError(f"買い目の書式が不正です（例 3t:1-2-3）: {spec}")
    kind, formation = spec.split(":", 1)
    bet_type = BET_ALIASES.get(kind.strip().lower()) or BET_ALIASES.get(kind.strip())
    if bet_type is None:
        raise ValueError(f"未対応の券種です: {kind}")
    size = BET_TYPES[bet_type][1]
    ordered = BET_TYPES[bet_type][2]
    groups = [g.strip() for g in formation.split("-")]
    if len(groups) != size:
        raise ValueError(f"{BET_TYPES[bet_type][0]} は {size} 着分の指定が必要です: {spec}")
    lanes = []
    for g in groups:
        g = "123456" if g.lower() == "all" else g
        if not g or any(ch not in "123456" for ch in g):
            raise ValueError(f"艇番は 1〜6 で指定してください: {spec}")
        lanes.append(sorted(set(g)))
    combos: list[str] = []
    for picks in itertools.product(*lanes):
        if len(set(picks)) != size:
            continue
        key = picks if ordered else tuple(sorted(picks))
        combo = "-".join(key)
        if combo not in combos:
            combos.append(combo)
    if not combos:
        raise ValueError(f"有効な組番がありません: {spec}")
    return bet_type, combos


@dataclass
class BacktestResult:
    spec: str
    bet_type: str
    points: int           # 1 レースあたりの点数
    races: int = 0
    hits: int = 0
    invested: int = 0
    returned: int = 0
    max_payout: int = 0
    max_losing_streak: int = 0

    @property
    def hit_rate(self) -> float:
        return self.hits / self.races if self.races else 0.0

    @property
    def recovery_rate(self) -> float:
        return self.returned / self.invested if self.invested else 0.0

    @property
    def profit(self) -> int:
        return self.returned - self.invested


def backtest(races: list[Race], spec: str, stake: int = 100) -> BacktestResult:
    """全レースで同じ買い目を 1 点 stake 円ずつ買い続けた場合の成績。"""
    bet_type, combos = parse_bet(spec)
    result = BacktestResult(spec=spec, bet_type=bet_type, points=len(combos))
    streak = 0
    for race in sorted(races, key=lambda r: r.key):
        paid = dict(race.payouts.get(bet_type, []))
        if not paid:  # 払戻情報が無い（不成立・返還など）レースは対象外
            continue
        result.races += 1
        result.invested += stake * len(combos)
        won = sum(paid.get(c, 0) for c in combos) * stake // 100
        if won:
            result.hits += 1
            result.returned += won
            result.max_payout = max(result.max_payout, won)
            streak = 0
        else:
            streak += 1
            result.max_losing_streak = max(result.max_losing_streak, streak)
    return result


# ---------------------------------------------------------------- 選手別

@dataclass
class RacerStat:
    racer_id: str
    name: str
    starts: int = 0
    first: int = 0
    top2: int = 0
    course1_starts: int = 0
    course1_first: int = 0

    @property
    def win_rate(self) -> float:
        return self.first / self.starts if self.starts else 0.0

    @property
    def course1_win_rate(self) -> float | None:
        return self.course1_first / self.course1_starts if self.course1_starts else None


def racer_stats(races: list[Race], min_starts: int = 30) -> list[RacerStat]:
    stats: dict[str, RacerStat] = {}
    for race in races:
        for e in race.entries:
            if e.status.startswith("K"):
                continue
            s = stats.setdefault(e.racer_id, RacerStat(e.racer_id, e.name))
            s.starts += 1
            s.first += e.position == 1
            s.top2 += bool(e.position and e.position <= 2)
            if (e.course or e.lane) == 1:
                s.course1_starts += 1
                s.course1_first += e.position == 1
    ranked = [s for s in stats.values() if s.starts >= min_starts]
    return sorted(ranked, key=lambda s: s.win_rate, reverse=True)


def stadium_course1_rates(races: list[Race]) -> list[tuple[str, int, float]]:
    """場ごとの 1 コース 1 着率。 (場名, レース数, 1着率)"""
    per: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for race in races:
        order = race.finish_order()
        if not order:
            continue
        per[race.stadium_code][0] += 1
        per[race.stadium_code][1] += race.course_of(order[0]) == 1
    rows = [(STADIUMS.get(c, c), n, w / n) for c, (n, w) in per.items()]
    return sorted(rows, key=lambda r: r[2], reverse=True)
