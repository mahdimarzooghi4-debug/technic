"""Experimental cash vs. invested-asset accounting for cohort scenarios; NOT production finance."""
from dataclasses import dataclass
from decimal import Decimal, localcontext
from pricing_lab import InvalidScenario, dec

@dataclass(frozen=True)
class LiquidityPeriod:
    """Order: revalue assets, liquidate, inflows, invest, pay expenses/capital."""
    asset_return: str = "0"
    invest_cash: str = "0"
    liquidate_value: str = "0"
    external_cash_in: str = "0"
    theory_support_paid: str = "0"
    host_paid: str = "0"
    other_paid: str = "0"
    capital_recipients: int = 0

@dataclass(frozen=True)
class LiquidityScenario:
    learner_count: int
    periods: tuple[LiquidityPeriod, ...]
    initial_cash_cost: str = "0"
    minimum_final_unrestricted_cash: str = "0"
    minimum_final_total_value: str = "0"

@dataclass(frozen=True)
class LiquiditySnapshot:
    period: int
    cash: Decimal
    invested_value: Decimal
    combined_value: Decimal
    cumulative_capital_paid: Decimal

@dataclass(frozen=True)
class LiquidityTrial:
    price: Decimal
    snapshots: tuple[LiquiditySnapshot, ...]
    cash_shortfall_periods: tuple[int, ...]
    final_cash: Decimal
    final_invested_value: Decimal
    final_total_value: Decimal
    capital_paid: Decimal
    feasible: bool

def validate_liquidity(s):
    if type(s.learner_count) is not int or s.learner_count <= 0:
        raise InvalidScenario("learner_count must be a positive integer")
    if not s.periods:
        raise InvalidScenario("At least one period required")
    for key in ("initial_cash_cost", "minimum_final_unrestricted_cash", "minimum_final_total_value"):
        if dec(getattr(s, key)) < 0:
            raise InvalidScenario(key + " cannot be negative")
    count = 0
    for period in s.periods:
        if type(period.capital_recipients) is not int or period.capital_recipients < 0:
            raise InvalidScenario("capital_recipients must be a nonnegative integer")
        count += period.capital_recipients
        if dec(period.asset_return) < -1:
            raise InvalidScenario("asset_return cannot be below -100%")
        for key in ("invest_cash", "liquidate_value", "external_cash_in",
                    "theory_support_paid", "host_paid", "other_paid"):
            if dec(getattr(period, key)) < 0:
                raise InvalidScenario(key + " cannot be negative")
    if count > s.learner_count:
        raise InvalidScenario("capital recipients exceed cohort size")

def simulate_liquidity(s, tuition):
    """Return detailed snapshots; paper gains never automatically become spendable cash.

    Negative cash flags failure even when later inflows cure the shortfall.
    Liquidation is explicit, limited to available marked asset value.
    This is NOT a licensed fund ledger, financial statement or real-money pricing policy.
    """
    validate_liquidity(s)
    p = dec(tuition)
    if p < 0:
        raise InvalidScenario("tuition cannot be negative")
    with localcontext() as ctx:
        ctx.prec = 36
        cash = p * s.learner_count - dec(s.initial_cash_cost)
        invested = Decimal(0)
        capital = Decimal(0)
        snapshots = [LiquiditySnapshot(0, cash, invested, cash + invested, capital)]
        shortages = [0] if cash < 0 else []
        for n, period in enumerate(s.periods, 1):
            invested *= (Decimal(1) + dec(period.asset_return))
            sale = dec(period.liquidate_value)
            if sale > invested:
                raise InvalidScenario(f"period {n}: asset liquidation exceeds invested value")
            invested -= sale
            cash += sale + dec(period.external_cash_in)
            contribution = dec(period.invest_cash)
            cash -= contribution
            invested += contribution
            capital += p * period.capital_recipients
            cash -= (dec(period.theory_support_paid) + dec(period.host_paid)
                     + dec(period.other_paid) + p * period.capital_recipients)
            if cash < 0:
                shortages.append(n)
            snapshots.append(LiquiditySnapshot(n, cash, invested, cash + invested, capital))
        feasible = (not shortages
                    and cash >= dec(s.minimum_final_unrestricted_cash)
                    and cash + invested >= dec(s.minimum_final_total_value))
        return LiquidityTrial(p, tuple(snapshots), tuple(shortages),
                              cash, invested, cash + invested, capital, feasible)
