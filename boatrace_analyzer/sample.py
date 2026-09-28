"""動作確認用のサンプルデータ生成。

実データの傾向（1コースの1着率が約5割など）に寄せた確率モデルで着順を決め、
払戻金は「還元率 75% ÷ 的中確率」にばらつきを加えて作る。
あくまで架空のデータで、実際のレース結果ではない。
"""

from __future__ import annotations

import itertools
import math
import random
from datetime import date, timedelta

from .models import STADIUMS, Entry, Race

# コースごとの基本の強さ（Plackett-Luce モデル）。1着率がおよそ 55/14/12/11/6/2 % になる
COURSE_STRENGTH = [1.0, 0.25, 0.22, 0.19, 0.11, 0.04]
RETURN_RATE = 0.75

SURNAMES = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤",
            "吉田", "山田", "松本", "井上", "木村", "林", "清水", "山崎", "森", "池田"]
GIVEN = ["翔太", "大輔", "健太", "拓也", "隆", "誠", "亮", "直樹", "悠斗", "和也", "美咲", "結衣"]


def _order_prob(order: tuple[int, ...], weights: dict[int, float]) -> float:
    """Plackett-Luce で、指定した艇が指定順に上位へ来る確率。"""
    remaining = sum(weights.values())
    p = 1.0
    for lane in order:
        p *= weights[lane] / remaining
        remaining -= weights[lane]
    return p


def _payout(prob: float, rng: random.Random) -> int:
    odds = RETURN_RATE / prob * math.exp(rng.gauss(0, 0.25))
    return max(100, int(round(odds * 100 / 10)) * 10)


def generate(n_races: int = 3000, seed: int = 1, start: date = date(2025, 1, 1)) -> list[Race]:
    rng = random.Random(seed)
    racers = [
        (f"{4000 + i:04d}", rng.choice(SURNAMES) + rng.choice(GIVEN), rng.lognormvariate(0, 0.35))
        for i in range(600)
    ]
    races: list[Race] = []
    codes = list(STADIUMS)
    day = 0
    while len(races) < n_races:
        d = (start + timedelta(days=day)).isoformat()
        for code in rng.sample(codes, 12):
            for race_no in range(1, 13):
                picked = rng.sample(racers, 6)
                weights = {lane: COURSE_STRENGTH[lane - 1] * picked[lane - 1][2] for lane in range(1, 7)}
                # 着順を Plackett-Luce で抽選
                order: list[int] = []
                pool = dict(weights)
                while pool:
                    r = rng.random() * sum(pool.values())
                    for lane, w in pool.items():
                        r -= w
                        if r <= 0:
                            break
                    order.append(lane)
                    del pool[lane]

                entries = []
                for lane in range(1, 7):
                    rid, name, _ = picked[lane - 1]
                    entries.append(Entry(
                        lane=lane, racer_id=rid, name=name,
                        motor=str(rng.randint(10, 80)), boat=str(rng.randint(10, 80)),
                        exhibit=round(rng.uniform(6.60, 6.95), 2), course=lane,
                        start=round(rng.uniform(0.05, 0.25), 2),
                        position=order.index(lane) + 1, status=f"{order.index(lane) + 1:02d}",
                    ))

                o = tuple(order)
                trio_p = sum(_order_prob(p, weights) for p in itertools.permutations(o[:3]))
                quin_p = _order_prob(o[:2], weights) + _order_prob(o[1::-1], weights)
                payouts = {
                    "win": [(str(o[0]), _payout(_order_prob(o[:1], weights), rng))],
                    "exacta": [(f"{o[0]}-{o[1]}", _payout(_order_prob(o[:2], weights), rng))],
                    "quinella": [("-".join(map(str, sorted(o[:2]))), _payout(quin_p, rng))],
                    "trifecta": [("-".join(map(str, o[:3])), _payout(_order_prob(o[:3], weights), rng))],
                    "trio": [("-".join(map(str, sorted(o[:3]))), _payout(trio_p, rng))],
                }
                races.append(Race(date=d, stadium_code=code, race_no=race_no,
                                  race_name="一般", distance=1800, entries=entries, payouts=payouts))
                if len(races) >= n_races:
                    return races
        day += 1
    return races
