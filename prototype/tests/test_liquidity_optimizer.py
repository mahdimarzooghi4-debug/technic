import unittest
from decimal import Decimal
from liquidity_lab import LiquidityPeriod as Period, LiquidityScenario as Scenario
from liquidity_optimizer import LiquidityCase, PriceRange, evaluate_prices
from pricing_lab import InvalidScenario

class LiquidityOptimizerTests(unittest.TestCase):
    def test_first_grid_price_and_capital_parity(self):
        s = Scenario(2, (Period(host_paid="10", capital_recipients=1),))
        r = evaluate_prices(PriceRange("0", "30", "5"), (LiquidityCase("base", s),))
        self.assertEqual(r["tested"], 7)
        self.assertEqual(r["first_feasible"], Decimal("10"))
        self.assertEqual(r["all_feasible"], (Decimal("10"), Decimal("15"), Decimal("20"), Decimal("25"), Decimal("30")))
        self.assertFalse(r["is_continuous_optimum"])

    def test_stress_envelope_and_diagnostics(self):
        base = Scenario(2, (Period(host_paid="10", capital_recipients=1),))
        stress = Scenario(2, (Period(host_paid="20", capital_recipients=1),))
        r = evaluate_prices(PriceRange("0", "30", "5"), (LiquidityCase("base", base), LiquidityCase("stress", stress)))
        self.assertEqual(r["first_feasible"], Decimal("20"))
        bad = next(x for x in r["rejected"] if x["price"] == Decimal("15"))
        self.assertEqual(bad["cases"][1]["violations"], ("INTERIM_CASH_DEFICIT", "FINAL_CASH_TARGET", "FINAL_VALUE_TARGET"))

    def test_illiquid_asset_does_not_fund_payments(self):
        s = Scenario(1, (Period(invest_cash="100"), Period(asset_return="1", host_paid="10")))
        r = evaluate_prices(PriceRange("100", "110", "10"), (LiquidityCase("illiquid", s),))
        self.assertEqual(r["first_feasible"], Decimal("110"))
        self.assertEqual(r["rejected"][0]["cases"][0]["trial"].final_invested_value, Decimal("200"))

    def test_final_value_target_separate_from_cash(self):
        s = Scenario(1, (Period(invest_cash="50"),), minimum_final_total_value="100")
        r = evaluate_prices(PriceRange("50", "100", "25"), (LiquidityCase("value", s),))
        self.assertEqual(r["first_feasible"], Decimal("100"))
        self.assertIn("FINAL_VALUE_TARGET", r["rejected"][0]["cases"][0]["violations"])

    def test_no_feasible_grid_point_not_global_proof(self):
        s = Scenario(1, (Period(host_paid="1000", capital_recipients=1),))
        r = evaluate_prices(PriceRange("0", "20", "5"), (LiquidityCase("no", s),))
        self.assertEqual(r["status"], "NO_FEASIBLE_GRID_POINT")
        self.assertIsNone(r["first_feasible"])

    def test_bad_inputs_fail_closed(self):
        s = Scenario(1, (Period(),))
        for grid in (PriceRange("10", "1", "1"), PriceRange("0", "10", "0"), PriceRange("-1", "10", "1"), PriceRange("0", "1000000", "0.1")):
            with self.assertRaises(InvalidScenario):
                evaluate_prices(grid, (LiquidityCase("base", s),))
        with self.assertRaises(InvalidScenario):
            evaluate_prices(PriceRange("0", "10", "1"), ())
        with self.assertRaises(InvalidScenario):
            evaluate_prices(PriceRange("0", "10", "1"), (LiquidityCase("x", s), LiquidityCase("x", s)))
        with self.assertRaises(InvalidScenario):
            evaluate_prices(PriceRange("0", "10", "1"), (LiquidityCase("x", Scenario(0,(Period(),))),))

if __name__ == "__main__":
    unittest.main()
