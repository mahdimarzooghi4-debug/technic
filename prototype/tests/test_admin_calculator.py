import unittest
from admin_calculator import solve_payload
from pricing_lab import InvalidScenario

def data():
    return {"course_version":"DEMO-v1","unknown":"P",
        "known":{"N":"2","G":"1.2","q":"0.8","C":"20"},
        "lower":"0","upper":"50","step":"5",
        "reasonable_lower":"30","reasonable_upper":"40",
        "constraints":[{"name":"economic","left":"N * P * (G - q)",
                         "operator":">=","right":"C"}]}

class CalculatorApiTests(unittest.TestCase):
    def test_declared_reasonableness_and_json(self):
        r=solve_payload(data())
        self.assertEqual(r["first_feasible"],"25")
        self.assertEqual(r["first_reasonable"],"30")
        self.assertEqual(r["reasonable_count"],3)
        self.assertEqual(r["status"],"REASONABLE_GRID_POINT_FOUND")
        self.assertFalse(r["empirical_reasonableness_certified"])
        self.assertFalse(r["continuous_solution_certified"])

    def test_swappable_unknown(self):
        p=data();p["unknown"]="N"
        p["known"]={"P":"10","G":"1.2","q":"0.8","C":"20"}
        p["reasonable_lower"]=None;p["reasonable_upper"]=None
        self.assertEqual(solve_payload(p)["first_feasible"],"5")

    def test_infeasible_vs_outside_bounds(self):
        p=data();p["upper"]="10"
        self.assertEqual(solve_payload(p)["status"],"NO_MATHEMATICALLY_FEASIBLE_GRID_POINT")
        p["upper"]="40";p["reasonable_lower"]="45";p["reasonable_upper"]="50"
        self.assertEqual(solve_payload(p)["status"],"NO_REASONABLE_GRID_POINT")

    def test_bad_payloads_fail_closed(self):
        for change in ({"unknown_key":1},{"known":{"N":2.5}},
                       {"constraints":[{"name":"x","left":"__import__('os')","operator":">=","right":"0"}]},
                       {"constraints":[{"left":"P"}]}):
            p=data();p.update(change)
            with self.assertRaises(InvalidScenario):
                solve_payload(p)

    def test_report_limit_and_counts(self):
        p=data();p.update(lower="0",upper="100",step="1")
        r=solve_payload(p)
        self.assertEqual(r["tested"],101)
        self.assertLessEqual(len(r["rejection_examples"]),20)
        self.assertLessEqual(len(r["feasible_examples"]),40)
        self.assertEqual(r["feasible_count"]+sum(r["rejection_counts"].values()),101)

if __name__=="__main__":
    unittest.main()
