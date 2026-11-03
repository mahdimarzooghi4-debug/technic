# Technic — Numerical Pricing Lab (experimental)

**Status: DRAFT / RESEARCH ONLY.** This is a small deterministic, pure-Python prototype and is NOT an approved tuition policy, an audited profit model, fund ledger, payment processor or a Production service.

## Goal
Model the confirmed Technic target: tuition paid at the start, theoretical/support and company-host payments during training, and employment capital equal to each successful learner's tuition. Explore whether a **provided** grid of tuition prices covers all modeled outflows while leaving a user-specified residual cash target and avoiding interim liquidity deficits.

## Run tests
From repository root:

```sh
cd prototype
python -m unittest discover -s tests -v
```

Requires Python 3.11+ standard library only. All numerical values in the tests are **artificial**, not Technic assumptions, tuition recommendations, profit margins or observed rates.

## API
- `Scenario(learner_count, periods, min_profit, price_min, price_max, price_step, initial_fixed_cost='0')`
- `Period(return_rate, theory_and_support, apprenticeship_hosts, other_costs, eligible_capital_recipients, other_unrestricted_inflow='0')`
- `simulate(scenario, price)`: returns end-of-period cash balances, minimum liquidity, capital paid and whether modeled constraints pass.
- `search_grid(scenario)`: scans an explicitly bounded price grid, returns first feasible **grid point** or `NO_FEASIBLE_GRID_POINT`. It does **not** prove global mathematical infeasibility between grid points or outside the bounded range.

Input monetary values and rates should be decimal strings in one explicitly chosen monetary unit (e.g. IRR). Floats are rejected. All returns in this experiment are assumed **realized and fully liquid within each period**, applied before outflows; this is an experimental assumption, **not a statement about Technic's fund**. There is no automatic period duration/rate conversion, no stochastic modeling, and no per-individual payment ledger.

`min_profit` is presently only a **minimum residual cash balance**, not GAAP/IFRS net income. A real accounting model must separately establish legal ownership of tuition principal, assets, liabilities, realized returns, taxes, and accessible liquidity.

## Limits / future contract gates
1. Business Contract PR #1 and Mathematical Spec PR #2 are DRAFT and have not been approved or merged.
2. Required before realistic calibration: exam/retake/refund policies; hosting-company payment schedules; timing and obligations for hiring incentives; independent-worker capital; legal fund custody and loss allocation; permitted investment returns and liquidity; actual cash-flow timing and verified sample data.
3. Fixed learner count is supplied; demand elasticity and uncertainty are absent.
4. A price cannot be treated as approved even when `feasible=True`; there is no transfer of money.
5. A grid with zero feasible points is **not** proof no feasible price exists anywhere.
6. No AI-selected variables, automated employment, guaranteed investment returns, or production deployment.

The source of confirmed decisions remains `docs/DECISIONS.md`. Numerical assumptions and example amounts are not decisions.
