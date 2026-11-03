import unittest
from decimal import Decimal

from pricing_lab import InvalidScenario, Period, Scenario, simulate
from scenario_analysis import (
    NamedScenario, delay_capital, scenario_envelope, sensitivity_at_price, shock_return
)


def baseline():
    return Scenario(
        learner_count=2,
        periods=(
            Period("0.1", "10", "5", "0", 0),
            Period("0.1", "10", "5", "0", 1),
        ),
        min_profit="20", price_min="10", price_max="100", price_step="5"
    )


class ScenarioAnalysisTests(unittest.TestCase):
    def test_envelope_requires_feasibility_for_every_case(self):
        base = baseline()
        loss = shock_return(base, 1, "-0.1")
        result = scenario_envelope((NamedScenario("baseline", base), NamedScenario("loss", loss)))
        self.assertEqual(result["tested"], 19)
        self.assertEqual(result["scenario_count"], 2)
        self.assertEqual(result["status"], "COMMON_FEASIBLE_GRID_PRICE")
        self.assertEqual(result["first_common_price"], Decimal("50"))
        for p, trials in result["per_price"]:
            if p in result["common_feasible_prices"]:
                self.assertTrue(all(trial.feasible for _, trial in trials))

    def test_no_common_grid_price_not_global_proof(self):
        base = baseline()
        impossible = Scenario(
            2, (Period("0", "10000", "0", "0", 2),),
            "20", "10", "100", "5")
        r = scenario_envelope((NamedScenario("base", base), NamedScenario("stress", impossible)))
        self.assertEqual(r["status"], "NO_COMMON_GRID_PRICE")
        self.assertIsNone(r["first_common_price"])

    def test_sensitivity_comparison_is_at_same_price(self):
        base = baseline()
        loss = shock_return(base, 0, "-0.2")
        result = sensitivity_at_price(base, "50", (NamedScenario("loss", loss),))
        self.assertEqual(result["price"], Decimal("50"))
        self.assertEqual(result["comparisons"][0]["final_balance_delta"], Decimal("-33.00"))
        self.assertEqual(result["comparisons"][0]["capital_delta"], 0)
        self.assertEqual(result["baseline"].final_balance, Decimal("39.50"))

    def test_delay_preserves_capital_recipients_and_changes_cash_timing(self):
        base = Scenario(2, (
            Period("0", "0", "0", "0", 1),
            Period("0", "0", "0", "0", 0),
        ), "0", "10", "50", "5")
        delayed = delay_capital(base, 0, 1, 1)
        a, b = simulate(base, "20"), simulate(delayed, "20")
        self.assertEqual(a.capital_paid, b.capital_paid)
        self.assertEqual(a.final_balance, b.final_balance)
        self.assertNotEqual(a.balances[1], b.balances[1])

    def test_invalid_shocks_fail_closed(self):
        base = baseline()
        with self.assertRaises(InvalidScenario):
            shock_return(base, 8, "0.1")
        with self.assertRaises(InvalidScenario):
            shock_return(base, 0, "-1.01")
        with self.assertRaises(InvalidScenario):
            delay_capital(base, 0, 1, 1)
        with self.assertRaises(InvalidScenario):
            scenario_envelope((
                NamedScenario("dup", base), NamedScenario("dup", base)))
        with self.assertRaises(InvalidScenario):
            scenario_envelope((
                NamedScenario("a", base),
                NamedScenario("b", Scenario(2, base.periods, "20", "10", "100", "3"))))

if __name__ == "__main__":
    unittest.main()
