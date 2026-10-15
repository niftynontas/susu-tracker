import unittest
from decimal import Decimal

from susu import Group, SusuError


def make_group():
    g = Group("50.00")
    for n in ("Ama", "Kofi", "Esi"):
        g.add_member(n)
    return g


class TestGroup(unittest.TestCase):
    def test_example_from_brief(self):
        g = make_group()
        g.record_contribution("Ama", "50")
        g.record_contribution("Kofi", "50")
        g.record_contribution("Esi", "30")
        res = g.close_week()
        self.assertFalse(res.closed)
        self.assertEqual(res.owing, {"Esi": Decimal("20.00")})
        self.assertEqual(g.current_week, 1)
        self.assertEqual(g.payouts, [])
        g.record_contribution("Esi", "20")
        res = g.close_week()
        self.assertTrue(res.closed)
        self.assertEqual(res.payout.recipient, "Ama")
        self.assertEqual(res.payout.amount, Decimal("150.00"))
        self.assertEqual(g.current_week, 2)
        self.assertEqual(g.report().next_recipient, "Kofi")

    def test_partial_payments_accumulate(self):
        g = make_group()
        self.assertEqual(g.record_contribution("Ama", "10.50"), Decimal("39.50"))
        self.assertEqual(g.record_contribution("Ama", "39.50"), Decimal("0.00"))

    def test_week_cannot_close_when_unpaid(self):
        g = make_group()
        g.record_contribution("Ama", "50")
        res = g.close_week()
        self.assertFalse(res.closed)
        self.assertEqual(res.owing["Kofi"], Decimal("50.00"))
        self.assertEqual(res.owing["Esi"], Decimal("50.00"))

    def test_reject_unknown_member(self):
        with self.assertRaises(SusuError):
            make_group().record_contribution("Yaw", "10")

    def test_reject_duplicate_member_case_insensitive(self):
        g = make_group()
        with self.assertRaises(SusuError):
            g.add_member("  ama ")

    def test_reject_zero_negative_and_bad_amounts(self):
        g = make_group()
        for bad in ("0", "-5", "abc", "1.234", "nan", "inf", 1.5):
            with self.assertRaises(SusuError, msg=str(bad)):
                g.record_contribution("Ama", bad)

    def test_reject_overpayment(self):
        g = make_group()
        g.record_contribution("Ama", "40")
        with self.assertRaises(SusuError):
            g.record_contribution("Ama", "10.01")

    def test_exact_money_no_float_errors(self):
        g = Group("0.30")
        g.add_member("A")
        g.record_contribution("A", "0.10")
        g.record_contribution("A", "0.20")
        self.assertEqual(g.amounts_owing(), {})

    def test_cannot_add_member_after_start(self):
        g = make_group()
        g.record_contribution("Ama", "10")
        with self.assertRaises(SusuError):
            g.add_member("Yaw")

    def test_only_current_week_contributions(self):
        g = make_group()
        with self.assertRaises(SusuError):
            g.record_contribution("Ama", "10", week=2)

    def test_full_cycle_then_locked(self):
        g = Group("10")
        g.add_member("A")
        g.add_member("B")
        for _ in range(2):
            g.record_contribution("A", "10")
            g.record_contribution("B", "10")
            self.assertTrue(g.close_week().closed)
        self.assertEqual([p.recipient for p in g.payouts], ["A", "B"])
        self.assertTrue(g.is_complete)
        with self.assertRaises(SusuError):
            g.close_week()
        with self.assertRaises(SusuError):
            g.record_contribution("A", "1")

    def test_cannot_close_empty_group(self):
        with self.assertRaises(SusuError):
            Group("10").close_week()

    def test_invalid_weekly_amount(self):
        for bad in ("0", "-1", "x"):
            with self.assertRaises(SusuError):
                Group(bad)


if __name__ == "__main__":
    unittest.main()
