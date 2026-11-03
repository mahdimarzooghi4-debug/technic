import unittest
from decimal import Decimal
from pricing_lab import InvalidScenario
from single_unknown_solver import Constraint, SingleUnknownCase, solve_grid

def case(**kwargs):
    data = dict(
        course_version="course-electricity-v1", unknown="P",
        known={"N": "2", "G": "1.2", "q": "0.8", "C": "20"},
        lower="0", upper="50", step="5",
        constraints=(Constraint("economic", "N * P * (G - q)", ">=", "C"),),
        reasonable_lower="30", reasonable_upper="40"
    )
    data.update(kwargs)
    return SingleUnknownCase(**data)

class SingleUnknownTests(unittest.TestCase):
    def test_solves_unknown_tuition_with_explicit_reasonableness(self):
        r = solve_grid(case())
        self.assertEqual(r["first_feasible"], Decimal("25"))
        self.assertEqual(r["first_reasonable"], Decimal("30"))
        self.assertEqual(r["reasonable_values"], (Decimal("30"), Decimal("35"), Decimal("40")))
        self.assertEqual(r["status"], "REASONABLE_GRID_POINT_FOUND")
        self.assertFalse(r["empirical_reasonableness_certified"])

    def test_can_solve_different_unknown(self):
        r = solve_grid(case(unknown="N", known={"P": "10", "G": "1.2", "q": "0.8", "C": "20"},
                            lower="1", upper="10", step="1", reasonable_lower=None, reasonable_upper=None))
        self.assertEqual(r["first_feasible"], Decimal("5"))

    def test_no_valid_math_and_no_reasonable_distinct(self):
        a = solve_grid(case(upper="10"))
        self.assertEqual(a["status"], "NO_MATHEMATICALLY_FEASIBLE_GRID_POINT")
        b = solve_grid(case(reasonable_lower="45", reasonable_upper="50", upper="40"))
        self.assertEqual(b["status"], "NO_REASONABLE_GRID_POINT")

    def test_multiple_non_monotonic_feasible_regions(self):
        r = solve_grid(case(known={}, lower="0", upper="6", step="1",
            constraints=(Constraint("outside", "(P - 2) * (P - 4)", ">=", "0"),),
            reasonable_lower=None, reasonable_upper=None))
        self.assertEqual(r["feasible_values"], tuple(Decimal(x) for x in (0, 1, 2, 4, 5, 6)))

    def test_undefined_point_is_not_mislabeled_as_infeasible(self):
        r = solve_grid(case(known={}, lower="0", upper="2", step="1",
            constraints=(Constraint("singularity", "1 / (P - 1)", ">=", "0"),),
            reasonable_lower=None, reasonable_upper=None))
        self.assertEqual(r["first_feasible"], Decimal("2"))
        self.assertEqual(r["rejected"][1]["status"], "UNDEFINED")

    def test_invalid_data_fail_closed(self):
        tests = (
            case(known={"P": "2"}),
            case(step="0"),
            case(known={"N": 1.5}),
            case(constraints=(Constraint("unsafe", "__import__('os')", ">=", "0"),)),
            case(constraints=(Constraint("unsafe", "P ** 20", ">=", "0"),)),
            case(constraints=(Constraint("missing", "X + P", ">=", "0"),)),
            case(constraints=(Constraint("bad", "P", ">", "10"),)),
            case(lower="0", upper="10000000", step="0.01"),
        )
        for item in tests:
            with self.subTest(case=item):
                with self.assertRaises(InvalidScenario):
                    solve_grid(item)

if __name__ == "__main__":
    unittest.main()
