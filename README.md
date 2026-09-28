# Hiromu-project

## 競艇（ボートレース）成績分析ツール `boatrace_analyzer`

BOAT RACE 公式サイトの競走成績データを取り込み、コース別成績・出目・買い目の的中率と回収率を集計する CLI ツールです。
Python 3.10 以上・標準ライブラリだけで動きます（LZH 展開用に `lhafile` を推奨）。

> **注意**: このツールは過去データの集計・検証用です。回収率 100% を超える買い方を保証するものではありません。
> 競艇の控除率は約 25% あり、同じ買い方を続けると長期的には回収率が 75% 前後に近づくのが普通です。

### 使い方

```bash
# 1. 公式サイトから競走成績を取得（自分の PC で実行。LZH 展開に lhafile を使う）
pip install lhafile
python -m boatrace_analyzer fetch --from 2025-09-01 --to 2025-09-30 --out data/raw

# 2. テキストを CSV（data/races.csv, data/entries.csv）に変換
python -m boatrace_analyzer parse data/raw --out data

# 3. 分析
python -m boatrace_analyzer report                      # 主要な分析をまとめて表示
python -m boatrace_analyzer courses --stadium 大村       # コース別 1着率・連対率・平均ST
python -m boatrace_analyzer stadiums                    # 場別のイン逃げ率
python -m boatrace_analyzer combos --type trifecta      # 3連単の出目ランキング
python -m boatrace_analyzer racers --min-starts 50      # 選手別 1着率
python -m boatrace_analyzer backtest --bet 3t:1-23-234 --bet win:1
```

分析コマンドは共通で `--data`（CSV の場所、既定 `data`）、`--stadium`（場名 or 場コード）、`--from` / `--to`（期間）で絞り込めます。

実データが無くても試せるよう、架空のサンプルデータも生成できます（1 コース 1 着率約 55%、還元率約 75% になるよう調整した乱数データ）。

```bash
python -m boatrace_analyzer sample --races 5000 --out data/sample
python -m boatrace_analyzer report --data data/sample
```

### 買い目の書式（backtest の `--bet`）

`券種:1着-2着-3着` の形で、各着の候補艇を並べます。

| 書式 | 意味 |
|---|---|
| `win:1` | 単勝 1 |
| `2t:1-2` | 2連単 1-2 |
| `2f:1-2` | 2連複 1=2 |
| `3t:1-2-3` | 3連単 1-2-3 |
| `3t:1-23-234` | 3連単フォーメーション（1 着 1、2 着 2・3、3 着 2・3・4 の 4 点） |
| `3t:1-all-all` | 3連単 1 着流し（20 点） |
| `3f:1-2-34` | 3連複（順不同、重複は自動で除外） |

結果には、的中率、投資額、払戻額、収支、回収率、最高払戻額、最大連敗数が出ます。

### 構成

| ファイル | 内容 |
|---|---|
| `boatrace_analyzer/fetch.py` | 公式サイト（`www1.mbrace.or.jp/od2/K/`）からのダウンロードと LZH 展開 |
| `boatrace_analyzer/parser.py` | 競走成績テキスト（Shift_JIS）のパーサー |
| `boatrace_analyzer/models.py` | データモデルと CSV 入出力 |
| `boatrace_analyzer/analysis.py` | 集計・バックテスト |
| `boatrace_analyzer/sample.py` | サンプルデータ生成 |
| `boatrace_analyzer/cli.py` | コマンドライン |

### テスト

```bash
python -m unittest -v
```
