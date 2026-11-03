"""Research-only, safe single-unknown inequality grid evaluator.

This is NOT a continuous solver, approval policy, or source of empirical bounds.
"""
import ast
from dataclasses import dataclass
from decimal import Decimal, localcontext
from pricing_lab import InvalidScenario, dec

MAX_POINTS = 20001
MAX_EXPRESSION_LENGTH = 1024
MAX_NODES = 128

@dataclass(frozen=True)
class Constraint:
    name: str
    left: str
    operator: str
    right: str

@dataclass(frozen=True)
class SingleUnknownCase:
    course_version: str
    unknown: str
    known: dict
    lower: str
    upper: str
    step: str
    constraints: tuple[Constraint, ...]
    reasonable_lower: str | None = None
    reasonable_upper: str | None = None

def _parse(expression, identifiers):
    if not isinstance(expression, str) or not expression.strip() or len(expression) > MAX_EXPRESSION_LENGTH:
        raise InvalidScenario("Invalid expression length")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise InvalidScenario("Invalid expression syntax") from exc
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_NODES:
        raise InvalidScenario("Expression too complex")
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub,
               ast.Mult, ast.Div, ast.USub, ast.UAdd, ast.Name, ast.Load,
               ast.Constant)
    for node in nodes:
        if not isinstance(node, allowed):
            raise InvalidScenario("Unsupported mathematical expression")
        if isinstance(node, ast.Name) and node.id not in identifiers:
            raise InvalidScenario("Unknown symbol: " + node.id)
        if isinstance(node, ast.Constant) and (type(node.value) is not int):
            raise InvalidScenario("Use integer literals and decimal-valued variables only")
    return tree

def _eval(node, values):
    if isinstance(node, ast.Expression):
        return _eval(node.body, values)
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.Constant):
        return Decimal(node.value)
    if isinstance(node, ast.UnaryOp):
        v = _eval(node.operand, values)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, ast.BinOp):
        a, b = _eval(node.left, values), _eval(node.right, values)
        if isinstance(node.op, ast.Add): return a + b
        if isinstance(node.op, ast.Sub): return a - b
        if isinstance(node.op, ast.Mult): return a * b
        if isinstance(node.op, ast.Div):
            if b == 0: raise InvalidScenario("Division by zero at trial price")
            return a / b
    raise InvalidScenario("Unsupported expression")

def validate_case(case):
    if not isinstance(case.course_version, str) or not case.course_version.strip():
        raise InvalidScenario("Course version required")
    if not isinstance(case.unknown, str) or not case.unknown.isidentifier() or case.unknown.startswith("_"):
        raise InvalidScenario("Valid unknown name required")
    if not isinstance(case.known, dict) or not case.constraints:
        raise InvalidScenario("Known values and constraints required")
    if case.unknown in case.known:
        raise InvalidScenario("Unknown cannot have a fixed value")
    identifiers = {case.unknown}
    fixed = {}
    for name, value in case.known.items():
        if not isinstance(name, str) or not name.isidentifier() or name.startswith("_"):
            raise InvalidScenario("Invalid known variable name")
        identifiers.add(name)
        fixed[name] = dec(value)
    lo, hi, step = dec(case.lower), dec(case.upper), dec(case.step)
    if lo > hi or step <= 0:
        raise InvalidScenario("Invalid search interval")
    with localcontext() as ctx:
        ctx.prec = 36
        count = int((hi - lo) // step) + 1
    if count > MAX_POINTS:
        raise InvalidScenario("Grid point limit exceeded")
    bounds = tuple(dec(v) if v is not None else None
                   for v in (case.reasonable_lower, case.reasonable_upper))
    if bounds[0] is not None and bounds[1] is not None and bounds[0] > bounds[1]:
        raise InvalidScenario("Inverted reasonableness bounds")
    if len(case.constraints) > 64:
        raise InvalidScenario("Too many constraints")
    compiled = []
    seen = set()
    for c in case.constraints:
        if not isinstance(c, Constraint) or not isinstance(c.name, str) or not c.name.strip() or c.name in seen:
            raise InvalidScenario("Each constraint needs a unique name")
        seen.add(c.name)
        if c.operator not in (">=", "<=", "=="):
            raise InvalidScenario("Unsupported inequality operator")
        compiled.append((c, _parse(c.left, identifiers), _parse(c.right, identifiers)))
    return fixed, lo, hi, step, count, bounds, compiled

def solve_grid(case):
    """Returns sampled feasible values, explicitly NOT a certified continuous solution.

    A singularity/undefined expression at one point is recorded as undefined,
    not silently misrepresented as a violated constraint.
    """
    fixed, lo, hi, step, count, bounds, compiled = validate_case(case)
    feasible, reasonable, rejected = [], [], []
    with localcontext() as ctx:
        ctx.prec = 36
        for i in range(count):
            value = lo + i * step
            variables = dict(fixed)
            variables[case.unknown] = value
            violations = []
            try:
                for c, left, right in compiled:
                    a, b = _eval(left, variables), _eval(right, variables)
                    satisfied = {">=": lambda: a >= b, "<=": lambda: a <= b, "==": lambda: a == b}[c.operator]()
                    if not satisfied:
                        violations.append(c.name)
            except (InvalidScenario, ArithmeticError) as exc:
                rejected.append({"value": value, "status": "UNDEFINED", "reason": str(exc)})
                continue
            if violations:
                rejected.append({"value": value, "status": "CONSTRAINT_FAILURE", "violations": tuple(violations)})
                continue
            feasible.append(value)
            if (bounds[0] is None or value >= bounds[0]) and (bounds[1] is None or value <= bounds[1]):
                reasonable.append(value)
            else:
                rejected.append({"value": value, "status": "OUTSIDE_DECLARED_REASONABLENESS_BOUNDS"})
    status = ("NO_MATHEMATICALLY_FEASIBLE_GRID_POINT" if not feasible else
              "NO_REASONABLE_GRID_POINT" if not reasonable else "REASONABLE_GRID_POINT_FOUND")
    return {"status": status, "unknown": case.unknown, "course_version": case.course_version,
            "first_feasible": feasible[0] if feasible else None,
            "first_reasonable": reasonable[0] if reasonable else None,
            "feasible_values": tuple(feasible), "reasonable_values": tuple(reasonable),
            "rejected": tuple(rejected), "tested": count,
            "continuous_solution_certified": False,
            "empirical_reasonableness_certified": False}
