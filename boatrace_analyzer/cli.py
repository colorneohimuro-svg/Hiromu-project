"""コマンドライン: python -m boatrace_analyzer <command> ..."""

from __future__ import annotations

import argparse
import sys
import unicodedata
from datetime import date
from pathlib import Path

from . import analysis, fetch, parser, sample
from .models import BET_TYPES, load_csv, save_csv

DEFAULT_BETS = ["win:1", "2t:1-2", "3t:1-2-3", "3t:1-23-234", "3t:1-all-all"]


def _width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def print_table(headers: list[str], rows: list[list[object]]) -> None:
    cells = [[str(c) for c in row] for row in [headers, *rows]]
    widths = [max(_width(row[i]) for row in cells) for i in range(len(headers))]
    for n, row in enumerate(cells):
        line = "  ".join(" " * (w - _width(c)) + c for c, w in zip(row, widths))
        print(line)
        if n == 0:
            print("-" * _width(line))


def pct(x: float | None) -> str:
    return "-" if x is None else f"{x * 100:.1f}%"


def load(args) -> list:
    data_dir = Path(args.data)
    if not (data_dir / "races.csv").exists():
        sys.exit(f"{data_dir}/races.csv がありません。先に parse か sample を実行してください")
    races = analysis.filter_races(load_csv(data_dir), args.stadium, args.date_from, args.date_to)
    if not races:
        sys.exit("条件に合うレースがありません")
    first, last = min(r.date for r in races), max(r.date for r in races)
    print(f"対象: {len(races)} レース（{first} 〜 {last}"
          f"{'、' + args.stadium if args.stadium else ''}）\n")
    return races


# ---------------------------------------------------------------- commands

def cmd_fetch(args) -> None:
    fetch.fetch_range(date.fromisoformat(args.date_from), date.fromisoformat(args.date_to),
                      Path(args.out), wait=args.wait)


def cmd_parse(args) -> None:
    races = []
    paths = []
    for p in map(Path, args.files):
        paths.extend(sorted(p.glob("[kK]*.[tT][xX][tT]")) if p.is_dir() else [p])
    for path in paths:
        parsed = parser.parse_file(path)
        print(f"{path.name}: {len(parsed)} レース")
        races.extend(parsed)
    save_csv(races, Path(args.out))
    print(f"\n{len(races)} レースを {args.out}/races.csv, entries.csv に保存しました")


def cmd_sample(args) -> None:
    races = sample.generate(args.races, seed=args.seed)
    save_csv(races, Path(args.out))
    print(f"架空のサンプルデータ {len(races)} レースを {args.out}/ に保存しました")


def cmd_courses(args, races=None) -> None:
    races = races or load(args)
    print("■ コース別成績")
    print_table(
        ["コース", "出走", "1着率", "2連対率", "3連対率", "平均ST"],
        [[s.course, s.starts, pct(s.rate(s.first)), pct(s.rate(s.top2)), pct(s.rate(s.top3)),
          "-" if s.avg_st is None else f"{s.avg_st:.2f}"] for s in analysis.course_stats(races)],
    )


def cmd_stadiums(args, races=None) -> None:
    races = races or load(args)
    print("■ 場別 1コース1着率（イン逃げ率）")
    print_table(["場", "レース", "1コース1着率"],
                [[name, n, pct(r)] for name, n, r in analysis.stadium_course1_rates(races)])


def cmd_combos(args, races=None) -> None:
    races = races or load(args)
    n, ranking = analysis.combo_ranking(races, args.type)
    label = BET_TYPES[args.type][0]
    print(f"■ {label} 出目ランキング（上位 {args.top}）")
    print("  回収率 = その出目を毎レース 100 円買い続けた場合")
    print_table(
        ["順位", "出目", "出現", "出現率", "平均配当", "回収率"],
        [[i, c.combo, c.hits, pct(c.hits / n), f"{c.avg_payout:,.0f}円",
          pct(c.total_payout / (100 * n))] for i, c in enumerate(ranking[: args.top], 1)],
    )


def cmd_backtest(args, races=None) -> None:
    specs = args.bet or DEFAULT_BETS
    for spec in specs:
        analysis.parse_bet(spec)  # データを読む前に書式エラーを出す
    races = races or load(args)
    print(f"■ バックテスト（1 点 {args.stake} 円で全レース購入した場合）")
    rows = []
    for spec in specs:
        r = analysis.backtest(races, spec, stake=args.stake)
        rows.append([spec, BET_TYPES[r.bet_type][0], r.points, r.races, pct(r.hit_rate),
                     f"{r.invested:,}", f"{r.returned:,}", f"{r.profit:+,}",
                     pct(r.recovery_rate), f"{r.max_payout:,}", r.max_losing_streak])
    print_table(["買い目", "券種", "点数", "レース", "的中率", "投資", "払戻", "収支",
                 "回収率", "最高払戻", "最大連敗"], rows)


def cmd_racers(args, races=None) -> None:
    races = races or load(args)
    stats = analysis.racer_stats(races, min_starts=args.min_starts)
    print(f"■ 選手別 1着率（出走 {args.min_starts} 回以上、上位 {args.top}）")
    print_table(
        ["順位", "登番", "選手", "出走", "1着率", "2連対率", "1コース1着率"],
        [[i, s.racer_id, s.name, s.starts, pct(s.win_rate), pct(s.top2 / s.starts),
          pct(s.course1_win_rate)] for i, s in enumerate(stats[: args.top], 1)],
    )


def cmd_report(args) -> None:
    races = load(args)
    for fn, extra in [(cmd_courses, {}), (cmd_stadiums, {}),
                      (cmd_combos, {"type": "trifecta", "top": 10}), (cmd_backtest, {"bet": None, "stake": 100})]:
        ns = argparse.Namespace(**vars(args), **extra)
        fn(ns, races)
        print()


# ---------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="boatrace_analyzer", description="競艇（ボートレース）成績分析ツール")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("fetch", help="公式サイトから競走成績をダウンロード")
    s.add_argument("--from", dest="date_from", required=True, help="開始日 YYYY-MM-DD")
    s.add_argument("--to", dest="date_to", required=True, help="終了日 YYYY-MM-DD")
    s.add_argument("--out", default="data/raw")
    s.add_argument("--wait", type=float, default=1.0, help="1 日ごとの待ち秒数")
    s.set_defaults(func=cmd_fetch)

    s = sub.add_parser("parse", help="競走成績テキストを CSV に変換")
    s.add_argument("files", nargs="+", help="kYYMMDD.TXT またはそれを含むディレクトリ")
    s.add_argument("--out", default="data")
    s.set_defaults(func=cmd_parse)

    s = sub.add_parser("sample", help="動作確認用の架空データを生成")
    s.add_argument("--races", type=int, default=5000)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--out", default="data/sample")
    s.set_defaults(func=cmd_sample)

    def analysis_cmd(name: str, help: str, func):
        s = sub.add_parser(name, help=help)
        s.add_argument("--data", default="data", help="races.csv のあるディレクトリ")
        s.add_argument("--stadium", help="場名（例: 大村）または場コード（例: 24）")
        s.add_argument("--from", dest="date_from", help="開始日 YYYY-MM-DD")
        s.add_argument("--to", dest="date_to", help="終了日 YYYY-MM-DD")
        s.set_defaults(func=func)
        return s

    analysis_cmd("courses", "コース別 1着率・連対率", cmd_courses)
    analysis_cmd("stadiums", "場別のイン逃げ率", cmd_stadiums)
    s = analysis_cmd("combos", "出目ランキング", cmd_combos)
    s.add_argument("--type", default="trifecta", choices=list(BET_TYPES))
    s.add_argument("--top", type=int, default=20)
    s = analysis_cmd("backtest", "買い目のバックテスト（的中率・回収率）", cmd_backtest)
    s.add_argument("--bet", action="append",
                   help="買い目（複数可）。例: 3t:1-23-234 / 2t:1-all / win:1。省略時は定番の買い目")
    s.add_argument("--stake", type=int, default=100, help="1 点あたりの金額")
    s = analysis_cmd("racers", "選手別成績", cmd_racers)
    s.add_argument("--min-starts", type=int, default=30)
    s.add_argument("--top", type=int, default=20)
    analysis_cmd("report", "主要な分析をまとめて表示", cmd_report)
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except ValueError as e:
        sys.exit(f"エラー: {e}")
