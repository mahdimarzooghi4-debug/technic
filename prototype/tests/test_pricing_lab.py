import unittest
from decimal import Decimal
from pricing_lab import Period, Scenario, InvalidScenario, simulate, search_grid

def scenario(**overrides):
    base = dict(learner_count=2, periods=(
        Period("0.1", "10", "5", "0", 0),
        Period("0.1", "10", "5", "0", 1)), min_profit="20",
        price_min="10", price_max="100", price_step="5")
    base.update(overrides)
    return Scenario(**base)

class LabTests(unittest.TestCase):
    def test_capital_equals_tuition_for_qualifying_recipient(self):
        trial = simulate(scenario(), "50")
        self.assertEqual(trial.capital_paid, Decimal("50"))
        self.assertEqual(trial.total_costs, Decimal("30"))
        self.assertEqual(trial.final_balance, Decimal("39.50"))
        self.assertEqual(trial.balances, (Decimal("100"), Decimal("95.0"), Decimal("39.50")))
        self.assertTrue(trial.feasible)

    def test_negative_interim_liquidity_fails_even_if_later_recovered(self):
        s = scenario(periods=(
            Period("0", "300", "0", "0", 0),
            Period("0", "0", "0", "0", 0, "500")), min_profit="0")
        trial = simulate(s, "50")
        self.assertGreater(trial.final_balance, 0)
        self.assertLess(trial.minimum_liquidity, 0)
        self.assertFalse(trial.feasible)

    def test_no_feasible_grid_price(self):
        s = scenario(periods=(Period("0", "1000", "0", "0", 2),))
        self.assertEqual(search_grid(s)["status"], "NO_FEASIBLE_GRID_POINT")

    def test_grid_determinism_and_first_price(self):
        a, b = search_grid(scenario()), search_grid(scenario())
        self.assertEqual(a["first_feasible"], b["first_feasible"])
        self.assertEqual(a["tested"], 19)
        self.assertEqual(a["first_feasible"].price, Decimal("40"))

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(InvalidScenario):
            simulate(scenario(), 10.5)
        with self.assertRaises(InvalidScenario):
            simulate(scenario(periods=(Period("-1.1", "0", "0", "0", 0),)), "50")
        with self.assertRaises(InvalidScenario):
            simulate(scenario(periods=(
                Period("0", "0", "0", "0", 2),
                Period("0", "0", "0", "0", 1))), "50")
        with self.assertRaises(InvalidScenario):
            search_grid(scenario(price_step="0.001"))

    def test_negative_fund_return(self):
        s = scenario(periods=(Period("-0.2", "0", "0", "0", 0),), min_profit="0")
        self.assertEqual(simulate(s, "100").final_balance, Decimal("160.0"))

if __name__ == "__main__":
    unittest.main()
