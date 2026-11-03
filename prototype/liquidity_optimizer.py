"""Bounded numerical price-grid feasibility for the segregated-liquidity lab.

A finite grid search is intentionally not a continuous solver, a certification
outside the chosen grid, a business price recommendation, or a payment approval.
"""
from dataclasses import dataclass
from decimal import Decimal, localcontext
from liquidity_lab import LiquidityScenario, simulate_liquidity, validate_liquidity
from pricing_lab import dec, InvalidScenario

MAX_GRID_POINTS = 20001

@dataclass(frozen=True)
class PriceRange:
    lower: str
    upper: str
    increment: str

@dataclass(frozen=True)
class LiquidityCase:
    label: str
    scenario: LiquidityScenario

def _grid(spec):
    lo, hi, step = (dec(spec.lower), dec(spec.upper), dec(spec.increment))
    if lo < 0 or hi < lo or step <= 0:
        raise InvalidScenario("price range must have 0 <= lower <= upper, increment > 0")
    with localcontext() as ctx:
        ctx.prec = 36
        count = int((hi - lo) // step) + 1
        if count > MAX_GRID_POINTS:
            raise InvalidScenario("grid exceeds maximum of 20001 prices")
        return tuple(lo + i * step for i in range(count))

def evaluate_prices(price_range, cases):
    """Search ALL supplied grid points, not just a monotonicity-based first root.

    If multiple cases are supplied, each price must satisfy every case. The
    cases are an explicitly supplied stress envelope, not a probability model.
    """
    cases = tuple(cases)
    if not cases:
        raise InvalidScenario("at least one case is required")
    labels = set()
    for case in cases:
        if not isinstance(case, LiquidityCase) or not isinstance(case.label, str) or not case.label.strip():
            raise InvalidScenario("every case requires a nonempty label")
        if case.label in labels:
            raise InvalidScenario("duplicate case label")
        labels.add(case.label)
        validate_liquidity(case.scenario)
    prices = _grid(price_range)
    feasible = []
    rejected = []
    for price in prices:
        rows = []
        for case in cases:
            trial = simulate_liquidity(case.scenario, price)
            failed = []
            if trial.cash_shortfall_periods:
                failed.append("INTERIM_CASH_DEFICIT")
            if trial.final_cash < dec(case.scenario.minimum_final_unrestricted_cash):
                failed.append("FINAL_CASH_TARGET")
            if trial.final_total_value < dec(case.scenario.minimum_final_total_value):
                failed.append("FINAL_VALUE_TARGET")
            rows.append({"case": case.label, "trial": trial, "violations": tuple(failed)})
        if all(not x["violations"] for x in rows):
            feasible.append(price)
        else:
            rejected.append({"price": price, "cases": tuple(rows)})
    return {
        "status": "FEASIBLE_ON_GRID" if feasible else "NO_FEASIBLE_GRID_POINT",
        "first_feasible": feasible[0] if feasible else None,
        "all_feasible": tuple(feasible),
        "tested": len(prices),
        "rejected": tuple(rejected),
        "cases": len(cases),
        "grid_max_tested": prices[-1],
        "is_continuous_optimum": False,
    }
