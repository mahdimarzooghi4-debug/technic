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

## Scenario analysis v0.2 (research)

`scenario_analysis.py` adds deterministic comparisons **without inventing probabilities**:

- `scenario_envelope((NamedScenario(label, scenario), ...))` scans an identical explicit tuition grid and returns the first price meeting all supplied scenarios, or `NO_COMMON_GRID_PRICE`. Neither status certifies continuous/global optimality or covers omitted real-world risks.
- `sensitivity_at_price(baseline, price, alternatives)` compares final residual cash, minimum modeled liquidity and total capital paid at the **same** tuition.
- `shock_return(scenario, period_index, new_rate)` replaces an explicit period return for a what-if test; it does not forecast returns.
- `delay_capital(scenario, from_period, to_period, recipients)` moves an already-scheduled recipient count to a later period without changing the total count or eligibility.

All prices, costs, return shocks, dates and period sizes must be supplied by a human/research scenario. The **same-period return-before-withdrawals convention** and assumption that returns are liquid remain research-only limitations. In a real fund, investment balances, spendable liquidity and legal obligations must be modeled separately, with finer timing when needed.

## Segregated liquidity research module (v0.3)

`liquidity_lab.py` is a separate **experimental** model: `LiquidityScenario`, `LiquidityPeriod`, `simulate_liquidity`. It distinguishes unrestricted **cash** from the **marked value of invested assets**. Unrealized investment gains or losses affect asset value but do not become available cash until an explicitly scheduled liquidation. Investing decreases free cash; asset liquidation transfers value back to cash without double-counting returns. Theory/support, apprenticeship-host costs, and tuition-equivalent capital for qualifying participants are cash outflows.

A cash shortfall in any period makes the trial infeasible even when later receipts restore the balance. Explicit sale amounts cannot exceed the available asset value. The model reports final cash, invested value, combined value, capital paid, and periods of modeled shortfall.

**Important limitations:** The period order is asset revaluation → liquidation → other cash inflow → new investment → expense/capital payment. All movements within one period are aggregated; negative intraperiod balances might be hidden, so real-world payments need transaction-timed checks. Asset prices, ability to liquidate, slippage, settlement delays and custody are **assumptions supplied by a scenario**, not facts or guarantees. The model does not establish actual fund ownership, legal reserves, future payment obligations, locked assets, payable taxes, accounting profit, or fiduciary authorizations. An available asset sale is not automatically permitted or executable. `feasible=True` is only feasibility under an explicit toy scenario, not clearance to use a tuition price.

Existing `pricing_lab.py` remains unchanged for regression compatibility and represents a more optimistic liquid-return experiment. It must **not** be used as the authoritative financial model when liquidity is material. Reconcile business contracts and obtain human sign-off before attempting actual pricing or any deployment.

## v0.4 — Bounded feasibility search on the segregated liquidity model

`liquidity_optimizer.py` exposes `evaluate_prices(PriceRange(lower, upper, increment), (LiquidityCase(label, LiquidityScenario(...)), ...))`. It evaluates **every explicitly supplied price grid point** against **every supplied scenario**, including cash shortages in any period, minimum unrestricted final cash and minimum final combined asset value. It reports the first feasible grid point and all feasible grid points, or `NO_FEASIBLE_GRID_POINT`; rejected points carry scenario-specific constraint violations.

- **No guessed financial inputs:** prices, return rates, learner counts, due-date cash outflows and asset liquidation schedules must all be supplied. Unit conventions are caller-owned and must be consistent.
- **No continuous/global optimality claim:** `first_feasible` means lowest among tested discrete points only. Zero feasible points does not imply infeasibility outside the grid, between grid points or under a different investment policy.
- **No approved business objective:** a required final cash target is not audited profit; no legal capital earmarking or balance-sheet liabilities are represented here.
- **No free investment liquidation:** invested wealth contributes to `final_total_value` but only an explicit permissible liquidation contributes to cash.
- **Non-forecast envelope:** all scenarios must be explicitly selected and audited by a human. Passing an envelope does not establish a probability-of-success claim.

Run `cd prototype && python -m unittest discover -s tests -v`. No production deployment, real fund, real returns or payment integration is authorized.

## v0.5 — Single-Unknown Course Inequality Calculator (research)

The confirmed product decision is `TEC-DEC-012` in `docs/DECISIONS.md`. The experimental `single_unknown_solver.py` introduces `SingleUnknownCase`, `Constraint`, and `solve_grid`.

For **each course version**, provide the selected unknown name (e.g. `P` for tuition or `N` for learners), fixed values for all other symbols, one or more inequalities (`>=`, `<=`, `==`), and an explicit finite `lower/upper/step` search grid. Optionally supply independently justified `reasonable_lower/reasonable_upper` bounds. The solver:
- rejects unknown symbols, multiple unresolved unknowns, floats, unsafe expression syntax, excessive grid sizes and invalid input;
- searches every grid point, including non-monotonic feasible regions, without assuming a single root;
- distinguishes mathematical constraint failures, undefined sample points, and values outside **caller-supplied** reasonable bounds;
- returns mathematically feasible sampled values and values within declared bounds separately.

**Critical:** an unbounded-by-evidence reasonable range is NOT empirical approval. Results are **sampled values only**, not exact continuous solutions, global optima, market realism, verified financial solvency, or approved prices. Expression inputs use strictly limited decimal arithmetic with operators `+`, `-`, `*`, `/`; no functions, arbitrary code, exponents, external data, stochastic inference, or business-rule modifications. A mathematical inequality like `N*P*(G-q)>=C` is illustrative only. A real course case must additionally connect to verified temporal cash flow, restricted liquidity, legal payment obligations, and validated data provenance.

The example parameters inside unit tests are fabricated *test fixtures*, not approved assumptions. Every revision of course inputs must be a separately versioned scenario and require a human decision before any commercial use.
