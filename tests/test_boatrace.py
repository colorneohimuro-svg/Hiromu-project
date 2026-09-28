import tempfile
import unittest
from pathlib import Path

from boatrace_analyzer import analysis, parser, sample
from boatrace_analyzer.models import load_csv, save_csv

FIXTURE = Path(__file__).parent / "fixtures" / "k250901.TXT"


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.races = parser.parse_file(FIXTURE)

    def test_races_and_date(self):
        self.assertEqual([r.race_no for r in self.races], [1, 2])
        self.assertEqual(self.races[0].date, "2025-09-01")
        self.assertEqual(self.races[0].stadium, "大村")
        self.assertEqual(self.races[0].distance, 1800)

    def test_entries(self):
        race = self.races[0]
        self.assertEqual(len(race.entries), 6)
        self.assertEqual(race.finish_order(), [1, 3, 2, 4, 6])
        first = race.entries[0]
        self.assertEqual((first.racer_id, first.name, first.exhibit, first.start),
                         ("4444", "山田太郎", 6.78, 0.12))
        flying = race.entries[-1]
        self.assertEqual((flying.status, flying.position, flying.start), ("F", None, -0.01))

    def test_course_differs_from_lane_and_absentee(self):
        race = self.races[1]
        self.assertEqual(race.course_of(2), 1)
        absent = race.entries[-1]
        self.assertEqual((absent.status, absent.course, absent.position), ("K0", None, None))

    def test_payouts(self):
        p = self.races[0].payouts
        self.assertEqual(p["win"], [("1", 150)])
        self.assertEqual(p["place"], [("1", 110), ("3", 240)])
        self.assertEqual(p["exacta"], [("1-3", 820)])
        self.assertEqual(p["wide"], [("1-3", 300), ("1-2", 180), ("2-3", 650)])
        self.assertEqual(p["trifecta"], [("1-3-2", 2340)])
        self.assertEqual(p["trio"], [("1-2-3", 620)])

    def test_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            save_csv(self.races, Path(tmp))
            loaded = load_csv(Path(tmp))
        self.assertEqual([r.payouts for r in loaded], [r.payouts for r in self.races])
        self.assertEqual([r.entries for r in loaded], [r.entries for r in self.races])


class BetTest(unittest.TestCase):
    def test_formation(self):
        self.assertEqual(analysis.parse_bet("3t:1-23-234")[1],
                         ["1-2-3", "1-2-4", "1-3-2", "1-3-4"])
        self.assertEqual(len(analysis.parse_bet("3t:1-all-all")[1]), 20)
        self.assertEqual(analysis.parse_bet("win:1"), ("win", ["1"]))

    def test_unordered_dedupes(self):
        self.assertEqual(analysis.parse_bet("3f:12-12-3")[1], ["1-2-3"])
        self.assertEqual(analysis.parse_bet("2f:2-1")[1], ["1-2"])

    def test_invalid(self):
        for spec in ["3t:1-2", "xx:1", "3t:1-1-1", "3t:1-2-7", "123"]:
            with self.assertRaises(ValueError, msg=spec):
                analysis.parse_bet(spec)


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.races = parser.parse_file(FIXTURE)

    def test_backtest(self):
        r = analysis.backtest(self.races, "3t:1-3-2")
        self.assertEqual((r.races, r.hits, r.invested, r.returned), (2, 1, 200, 2340))
        r = analysis.backtest(self.races, "2t:12-12")
        self.assertEqual((r.points, r.invested, r.returned), (2, 400, 1540))
        self.assertEqual(r.max_losing_streak, 1)

    def test_course_stats_uses_entry_course(self):
        stats = analysis.course_stats(self.races)
        c1 = stats[0]
        self.assertEqual((c1.starts, c1.first), (2, 2))  # 2R は 2 号艇が 1 コースから勝利
        self.assertEqual(stats[5].starts, 1)             # 2R の 6 号艇は欠場で除外

    def test_combo_ranking(self):
        n, ranking = analysis.combo_ranking(self.races, "trifecta")
        self.assertEqual(n, 2)
        self.assertEqual({c.combo for c in ranking}, {"1-3-2", "2-1-4"})

    def test_filter(self):
        self.assertEqual(len(analysis.filter_races(self.races, stadium="大村")), 2)
        self.assertEqual(len(analysis.filter_races(self.races, stadium="24", date_from="2025-09-02")), 0)
        with self.assertRaises(ValueError):
            analysis.filter_races(self.races, stadium="東京")


class SampleTest(unittest.TestCase):
    def test_realistic_shape(self):
        races = sample.generate(2000, seed=3)
        self.assertEqual(len(races), 2000)
        c1 = analysis.course_stats(races)[0]
        self.assertAlmostEqual(c1.first / c1.starts, 0.55, delta=0.05)
        r = analysis.backtest(races, "3t:all-all-all")
        self.assertEqual(r.hit_rate, 1.0)
        self.assertAlmostEqual(r.recovery_rate, 0.75, delta=0.08)


if __name__ == "__main__":
    unittest.main()
