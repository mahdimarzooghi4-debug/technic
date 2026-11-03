import unittest
from decimal import Decimal
from pricing_lab import InvalidScenario
from liquidity_lab import LiquidityPeriod as P, LiquidityScenario as S, simulate_liquidity, validate_liquidity

class LiquidityTests(unittest.TestCase):
    def test_paper_gain_cannot_pay_host(self):
        r = simulate_liquidity(S(1, (P(invest_cash="100"), P(asset_return="0.5", host_paid="20"))), "100")
        self.assertEqual(r.final_invested_value, Decimal("150"))
        self.assertEqual(r.final_cash, Decimal("-20"))
        self.assertEqual(r.cash_shortfall_periods, (2,))
        self.assertFalse(r.feasible)

    def test_explicit_asset_sale_funds_payment(self):
        r = simulate_liquidity(S(1, (P(invest_cash="100"), P(asset_return="0.5", liquidate_value="30", host_paid="20"))), "100")
        self.assertEqual(r.final_cash, Decimal("10"))
        self.assertEqual(r.final_invested_value, Decimal("120"))
        self.assertTrue(r.feasible)

    def test_capital_exactly_tuition_per_recipient(self):
        r = simulate_liquidity(S(3, (P(invest_cash="120"), P(liquidate_value="80", capital_recipients=2))), "40")
        self.assertEqual(r.capital_paid, Decimal("80"))
        self.assertEqual(r.final_total_value, Decimal("40"))
        self.assertTrue(r.feasible)

    def test_illiquid_value_not_cash(self):
        r = simulate_liquidity(S(1, (P(invest_cash="100"),), minimum_final_unrestricted_cash="10"), "100")
        self.assertEqual(r.final_total_value, Decimal("100"))
        self.assertFalse(r.feasible)

    def test_loss_and_cash_deficit(self):
        r = simulate_liquidity(S(1, (P(invest_cash="100"), P(asset_return="-0.5", liquidate_value="50", host_paid="51"))), "100")
        self.assertEqual(r.final_total_value, Decimal("-1"))
        self.assertFalse(r.feasible)

    def test_oversale_rejected(self):
        with self.assertRaises(InvalidScenario):
            simulate_liquidity(S(1, (P(liquidate_value="1"),)), "100")

    def test_repeated_recipients_rejected_at_cohort_bound(self):
        with self.assertRaises(InvalidScenario):
            validate_liquidity(S(1, (P(capital_recipients=1), P(capital_recipients=1))))

    def test_invalid_float_and_rate(self):
        with self.assertRaises(InvalidScenario):
            simulate_liquidity(S(1, (P(),)), 10.5)
        with self.assertRaises(InvalidScenario):
            simulate_liquidity(S(1, (P(asset_return="-1.01"),)), "100")

    def test_late_cash_does_not_erase_prior_shortfall(self):
        r = simulate_liquidity(S(1, (P(host_paid="150"), P(external_cash_in="200"))), "100")
        self.assertGreater(r.final_cash, 0)
        self.assertEqual(r.cash_shortfall_periods, (1,))
        self.assertFalse(r.feasible)

    def test_conservation_without_return(self):
        r = simulate_liquidity(S(2, (P(invest_cash="80", host_paid="10"), P(liquidate_value="20", capital_recipients=1))), "50")
        self.assertEqual(r.final_cash, Decimal("-20"))
        self.assertEqual(r.final_invested_value, Decimal("60"))
        self.assertEqual(r.final_total_value, Decimal("40"))
        self.assertFalse(r.feasible)

if __name__ == "__main__":
    unittest.main()
