"""Experimental deterministic cohort cash-flow pricing lab. Not production finance code."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext
from typing import Tuple

class InvalidScenario(ValueError):
    pass

def dec(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise InvalidScenario("Use decimal strings or integers; floats and booleans are forbidden")
    try:
        d = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise InvalidScenario("Invalid decimal input") from exc
    if not d.is_finite():
        raise InvalidScenario("Inputs must be finite")
    return d

@dataclass(frozen=True)
class Period:
    """Cash movements occur at period end; investment return is applied before outflows."""
    return_rate: str
    theory_and_support: str
    apprenticeship_hosts: str
    other_costs: str
    eligible_capital_recipients: int
    other_unrestricted_inflow: str = "0"

@dataclass(frozen=True)
class Scenario:
    learner_count: int
    periods: Tuple[Period, ...]
    min_profit: str
    price_min: str
    price_max: str
    price_step: str
    initial_fixed_cost: str = "0"

@dataclass(frozen=True)
class Trial:
    price: Decimal
    balances: tuple
    final_balance: Decimal
    minimum_liquidity: Decimal
    capital_paid: Decimal
    total_costs: Decimal
    feasible: bool

def validate(s: Scenario):
    if type(s.learner_count) is not int or s.learner_count <= 0:
        raise InvalidScenario("learner_count must be a positive integer")
    if not s.periods:
        raise InvalidScenario("At least one period is required")
    for label in ("min_profit", "price_min", "price_max", "price_step", "initial_fixed_cost"):
        value = dec(getattr(s, label))
        if value < 0 or (label == "price_step" and value == 0):
            raise InvalidScenario(f"{label} must be nonnegative; price_step positive")
    if dec(s.price_min) > dec(s.price_max):
        raise InvalidScenario("price_min > price_max")
    for period in s.periods:
        if type(period.eligible_capital_recipients) is not int or not (0 <= period.eligible_capital_recipients <= s.learner_count):
            raise InvalidScenario("Invalid capital recipient count")
        if dec(period.return_rate) < -1:
            raise InvalidScenario("Return below -100% is invalid")
        for label in ("theory_and_support", "apprenticeship_hosts", "other_costs", "other_unrestricted_inflow"):
            if dec(getattr(period, label)) < 0:
                raise InvalidScenario(f"{label} must be nonnegative")
    if sum(p.eligible_capital_recipients for p in s.periods) > s.learner_count:
        raise InvalidScenario("Duplicate/too many recipients across periods")
    nsteps = (dec(s.price_max) - dec(s.price_min)) / dec(s.price_step)
    if nsteps > 20000:
        raise InvalidScenario("Price grid too large (>20001 points)")

def simulate(s: Scenario, price) -> Trial:
    validate(s)
    p = dec(price)
    if p < 0:
        raise InvalidScenario("Negative tuition")
    with localcontext() as ctx:
        ctx.prec = 36
        balance = p * s.learner_count - dec(s.initial_fixed_cost)
        balances = [balance]
        capital_paid = Decimal(0)
        total_costs = dec(s.initial_fixed_cost)
        for period in s.periods:
            expenses = sum((dec(period.theory_and_support), dec(period.apprenticeship_hosts), dec(period.other_costs)), Decimal(0))
            cap = p * period.eligible_capital_recipients
            balance = balance * (Decimal(1) + dec(period.return_rate)) + dec(period.other_unrestricted_inflow) - expenses - cap
            balances.append(balance)
            capital_paid += cap
            total_costs += expenses
        minimum_liquidity = min(balances)
        final = balance
        # Final balance is residual cash after modeled payments, not audited net profit.
        feasible = minimum_liquidity >= 0 and final >= dec(s.min_profit)
        return Trial(p, tuple(balances), final, minimum_liquidity, capital_paid, total_costs, feasible)

def search_grid(s: Scenario):
    """Find first feasible GRID price; not a globally certified mathematical optimum."""
    validate(s)
    low, high, step = dec(s.price_min), dec(s.price_max), dec(s.price_step)
    results = []
    p = low
    while p <= high:
        results.append(simulate(s, p))
        p += step
    matches = [r for r in results if r.feasible]
    return {"status": "FEASIBLE_ON_GRID" if matches else "NO_FEASIBLE_GRID_POINT",
            "tested": len(results), "first_feasible": matches[0] if matches else None,
            "feasible_count": len(matches), "trials": tuple(results)}

if __name__ == "__main__":
    raise SystemExit("Import pricing_lab with explicit scenario inputs; no business defaults.")
