"""Experimental scenario-envelope and sensitivity analysis; no production decisions."""
from dataclasses import dataclass, replace
from decimal import Decimal

from pricing_lab import InvalidScenario, Scenario, dec, simulate, validate


@dataclass(frozen=True)
class NamedScenario:
    label: str
    scenario: Scenario


def _shared_grid(entries):
    """Comparable scenarios must use the same explicitly supplied price grid."""
    if not entries:
        raise InvalidScenario("At least one named scenario is required")
    labels = set()
    base = entries[0].scenario
    for entry in entries:
        if not isinstance(entry.label, str) or not entry.label.strip() or entry.label in labels:
            raise InvalidScenario("Scenario labels must be unique and nonempty")
        labels.add(entry.label)
        validate(entry.scenario)
        if any(dec(getattr(entry.scenario, field)) != dec(getattr(base, field))
               for field in ("price_min", "price_max", "price_step")):
            raise InvalidScenario("Scenarios require an identical price grid")
    return dec(base.price_min), dec(base.price_max), dec(base.price_step)


def scenario_envelope(entries):
    """Find prices feasible in every supplied scenario, with no invented probabilities.

    NO_COMMON_GRID_PRICE does not establish infeasibility outside the sampled grid.
    It does not claim the supplied scenarios exhaust real-world risks.
    """
    entries = tuple(entries)
    low, high, step = _shared_grid(entries)
    tested, feasible_prices, details = 0, [], []
    price = low
    while price <= high:
        trials = tuple((entry.label, simulate(entry.scenario, price)) for entry in entries)
        meets_all = all(result.feasible for _, result in trials)
        details.append((price, trials))
        if meets_all:
            feasible_prices.append(price)
        tested += 1
        price += step
    return {
        "status": "COMMON_FEASIBLE_GRID_PRICE" if feasible_prices else "NO_COMMON_GRID_PRICE",
        "first_common_price": feasible_prices[0] if feasible_prices else None,
        "common_feasible_prices": tuple(feasible_prices),
        "tested": tested,
        "per_price": tuple(details),
        "scenario_count": len(entries),
    }


def sensitivity_at_price(base: Scenario, price, alternatives):
    """Compare modeled results against a named baseline at the SAME tuition.

    Alternatives are explicit scenarios, not generated forecasts or likelihoods.
    No model changes pass/fail criteria or estimates probability.
    """
    validate(base)
    value = dec(price)
    baseline = simulate(base, value)
    labels = set()
    comparisons = []
    for alt in alternatives:
        if not isinstance(alt.label, str) or not alt.label.strip() or alt.label in labels:
            raise InvalidScenario("Sensitivity labels must be unique and nonempty")
        labels.add(alt.label)
        validate(alt.scenario)
        trial = simulate(alt.scenario, value)
        comparisons.append({
            "label": alt.label,
            "feasible": trial.feasible,
            "final_balance": trial.final_balance,
            "final_balance_delta": trial.final_balance - baseline.final_balance,
            "minimum_liquidity": trial.minimum_liquidity,
            "minimum_liquidity_delta": trial.minimum_liquidity - baseline.minimum_liquidity,
            "capital_paid": trial.capital_paid,
            "capital_delta": trial.capital_paid - baseline.capital_paid,
        })
    return {"price": value, "baseline": baseline, "comparisons": tuple(comparisons)}


def shock_return(base: Scenario, period_index: int, new_rate: str) -> Scenario:
    """Generate an explicit what-if return change; not a return prediction."""
    validate(base)
    if type(period_index) is not int or not (0 <= period_index < len(base.periods)):
        raise InvalidScenario("Invalid period index")
    rate = dec(new_rate)
    if rate < -1:
        raise InvalidScenario("Return below -100%")
    periods = list(base.periods)
    periods[period_index] = replace(periods[period_index], return_rate=str(rate))
    return replace(base, periods=tuple(periods))


def delay_capital(base: Scenario, from_period: int, to_period: int, recipients: int) -> Scenario:
    """Explicitly move scheduled capital recipients later, without altering eligibility."""
    validate(base)
    if (type(from_period) is not int or type(to_period) is not int or
            not (0 <= from_period < to_period < len(base.periods))):
        raise InvalidScenario("Delay must move between valid ordered periods")
    if type(recipients) is not int or recipients <= 0:
        raise InvalidScenario("Recipients must be a positive integer")
    periods = list(base.periods)
    if periods[from_period].eligible_capital_recipients < recipients:
        raise InvalidScenario("Cannot move more recipients than scheduled")
    periods[from_period] = replace(
        periods[from_period],
        eligible_capital_recipients=periods[from_period].eligible_capital_recipients - recipients)
    periods[to_period] = replace(
        periods[to_period],
        eligible_capital_recipients=periods[to_period].eligible_capital_recipients + recipients)
    return replace(base, periods=tuple(periods))
