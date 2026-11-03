# Technic — Decision Register

**Repository:** `mahdimarzooghi4-debug/technic`  
**Status:** Confirmed business decisions and explicitly open questions  
**Initial record:** 2026-11-03  
**Rule:** This register is the canonical record of confirmed product/business decisions. Proposals, assumptions, illustrative formulas, and historical document claims are not automatically approved decisions. Update decisions by a reviewed, traceable change; preserve history instead of silently rewriting it.

## Confirmed decisions

### TEC-DEC-001 — Product mission and scope
Technic (تکنیک) is an integrated ecosystem for skill acquisition, real-world apprenticeship, employment placement, and employment capital. It is **not** only a video-course website or a job board. Its learner journey connects training, competence assessment, practical experience, employment or self-employment, and financial support.

### TEC-DEC-002 — Asynchronous theoretical training
Theoretical course content is delivered offline/asynchronously through a digital learning platform. The intended learning experience has similarities to Coursera, Udemy, and edX; this comparison is a reference, not a decision to duplicate any provider.

### TEC-DEC-003 — Course learner support
Each enrolled jobseeker/learner has course support during theoretical learning. Detailed supporter responsibilities, service-level agreements, capacity limits, and costs remain to be specified.

### TEC-DEC-004 — Real-company apprenticeship and payments
Practical learning and apprenticeship take place in real participating companies. **Technic pays apprenticeship-host companies** for providing the practical learning placement; the payment amount, timing, and contractual duties are not yet defined.

### TEC-DEC-005 — Qualification before employment capital
Qualifying for employment capital requires passing both theoretical and practical assessments. Passing thresholds, retakes, appeals, withdrawal, and exception rules remain undefined.

### TEC-DEC-006 — Two employment pathways
After qualifying, a learner may pursue (a) placement with a hiring company or (b) independent work. Technic introduces qualified people to hiring companies; placement introduction is not automatically a guarantee of an employment contract.

### TEC-DEC-007 — Ownership and destination of capital
Employment capital is **attributable to and belongs to the qualified individual**. When they pursue employment, the amount is **paid to the hiring company as a hiring incentive on their behalf**. For independent work, it is **paid to the individual**. Legal ownership mechanics, conditions of disbursement, clawbacks, early termination, and employer obligations require explicit contracts; none are inferred.

### TEC-DEC-008 — Tuition enters the fund at the beginning
A learner pays course tuition at entry. Tuition is directed into a fund from the beginning and is intended to earn investment returns over time. The fund's legal form, custody, permitted investments, liquidity, return assumptions, loss allocation, and regulatory requirements are **not yet decided**.

### TEC-DEC-009 — Target of tuition pricing
The pricing design goal is to make **an amount equivalent to the learner's initial tuition** available as employment capital for each person who successfully completes both assessments, while covering all education, learner-support, company-apprenticeship, operating and fund costs and producing sustainable profit for Technic. This is a **target/constraint to test**, not a guaranteed return or a claim that all prices can satisfy it.

### TEC-DEC-010 — Numerical pricing is a core technical capability
The central differentiating technical challenge is a mathematically specified, time-dependent pricing and financial-feasibility model solved using appropriate numerical methods. Its inputs must be meaningful and grounded, including course duration, cash-flow timing, realized/assumed fund returns, costs, successful completions, and risks. The solver must be allowed to report **no feasible tuition** under the stated constraints. A calculated solution is not by itself proof of commercial viability or legal knowledge-based-company status.

### TEC-DEC-011 — Distinct payments and obligations
Payments to an apprenticeship-host company for practical training and payments to a hiring company as an employment incentive are **different financial events with different purposes**, even if the same company performs both roles. Account for them independently; do not double count fund principal, returns, costs or capital obligations.

## Open decisions — do not guess

1. Course-specific theoretical/practical duration, assessment thresholds, retakes, failure and refund treatment.
2. Exact apprenticeship-host payment rate, timing, acceptance criteria and evidence of practical training.
3. Capital release event, limits, legal beneficiary/custodian structure, employer hiring obligation, vesting, clawback and early departure treatment.
4. Fund authorization/legal structure, owner of contributed money, custody, liquidity constraints, investment and loss rules, fees/taxes, and approved risk limits.
5. Confirmed cost model, time-stamped cash flows, cohort timing, desired profit definition and pricing objective.
6. Empirically supported demand-versus-price, completion/placement rates, employer capacity, and realistic return distributions.
7. Course supporter and on-site mentor responsibilities, reporting, and service levels.
8. Whether historical spreadsheet/market-study references to ISA, BNPL or SNBL remain in scope; **do not treat historical assumptions as approved**. In particular, the earlier financial model explicitly says ISA is removed, while an older market analysis refers to ISA.
9. Details of any claimed employment or service-quality guarantee, liabilities, and third-party contractual protections.
10. Numerical algorithms, stochastic/risk constraints, parameter estimation, validation datasets and implementation technology; design selection follows mathematical specification and tests.

## Modeling and implementation safeguards

- Separate confirmed business decisions from research hypotheses and financial scenarios.
- Preserve each calculation's model version, dated assumptions, unit definitions, scenario, solver output, and review decision.
- Model **monthly or transaction-timed cash flows** rather than treating all tuition as invested for the full duration while also paying interim expenses.
- Report principal, investment returns, income, expenses, liabilities/earmarked employment capital, and free liquidity separately.
- Never promise a fixed return, automatic employment, or payment eligibility merely because an example equation produced a value.
- For software delivery use: Business → Technical → Scrum/Product Backlog → Sprint → Code → Code Review → Stage → QA/Testing → Release Approval → Production → Monitoring → Improvement.
- No code implementation, deployment, fund operation, money movement or legal claim is authorized by this document.

## Change control

For each new decision, record its stable ID, description, status (**CONFIRMED**, **PROPOSED**, **SUPERSEDED**), date, rationale, and superseding link where applicable. Only explicit business approval makes a proposal confirmed. Never silently promote numerical examples, prior assistant recommendations or older document assumptions into policy.
