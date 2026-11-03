"""Local-only exploratory HTTP interface for the Technic inequality lab.

Never expose this stdlib development server on public network or use for real pricing.
"""
from dataclasses import asdict
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json

from pricing_lab import InvalidScenario, dec
from single_unknown_solver import Constraint, SingleUnknownCase, solve_grid

MAX_BODY = 65536
ROOT = Path(__file__).resolve().parent
HTML = ROOT / "admin_calculator.html"


def _to_json(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, tuple):
        return [_to_json(x) for x in value]
    if isinstance(value, list):
        return [_to_json(x) for x in value]
    if isinstance(value, dict):
        return {key: _to_json(v) for key, v in value.items()}
    return value


def solve_payload(payload):
    """Validate request shape, delegate arithmetic to the existing solver."""
    if not isinstance(payload, dict):
        raise InvalidScenario("Expected a JSON object")
    allowed = {"course_version", "unknown", "known", "lower", "upper",
               "step", "constraints", "reasonable_lower", "reasonable_upper"}
    if set(payload) - allowed:
        raise InvalidScenario("Unknown request keys")
    raw_constraints = payload.get("constraints")
    if not isinstance(raw_constraints, list) or len(raw_constraints) > 64:
        raise InvalidScenario("constraints must be a JSON list of at most 64 items")
    constraints = []
    for row in raw_constraints:
        if not isinstance(row, dict) or set(row) != {"name", "left", "operator", "right"}:
            raise InvalidScenario("Each constraint requires name,left,operator,right")
        constraints.append(Constraint(**row))
    if not isinstance(payload.get("known"), dict):
        raise InvalidScenario("known must be an object")
    known = payload["known"]
    if any(not isinstance(v, str) for v in known.values()):
        raise InvalidScenario("Known values must be decimal strings")
    for key in ("lower", "upper", "step", "reasonable_lower", "reasonable_upper"):
        if key in payload and payload[key] is not None and not isinstance(payload[key], str):
            raise InvalidScenario(f"{key} must be a decimal string")
    for key in ("course_version", "unknown"):
        if not isinstance(payload.get(key), str):
            raise InvalidScenario(f"{key} is required as text")
    for key in ("lower", "upper", "step"):
        if key not in payload:
            raise InvalidScenario(f"{key} is required")
    case = SingleUnknownCase(
        course_version=payload["course_version"],
        unknown=payload["unknown"],
        known=known,
        lower=payload["lower"], upper=payload["upper"], step=payload["step"],
        constraints=tuple(constraints),
        reasonable_lower=payload.get("reasonable_lower"),
        reasonable_upper=payload.get("reasonable_upper"),
    )
    result = solve_grid(case)
    # Bound returned diagnostic rows, but keep exact counts and the first examples.
    reasons = {}
    for row in result["rejected"]:
        reason = row["status"]
        reasons[reason] = reasons.get(reason, 0) + 1
    return _to_json({
        "status": result["status"],
        "course_version": result["course_version"],
        "unknown": result["unknown"],
        "tested": result["tested"],
        "first_feasible": result["first_feasible"],
        "first_reasonable": result["first_reasonable"],
        "feasible_count": len(result["feasible_values"]),
        "reasonable_count": len(result["reasonable_values"]),
        "feasible_examples": result["feasible_values"][:40],
        "reasonable_examples": result["reasonable_values"][:40],
        "rejection_counts": reasons,
        "rejection_examples": result["rejected"][:20],
        "continuous_solution_certified": False,
        "empirical_reasonableness_certified": False,
        "warning": "Research grid results only; no real-market validation or financial approval.",
    })


class Handler(BaseHTTPRequestHandler):
    def _reply(self, status, body, mime):
        raw = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path != "/":
            self._reply(404, "Not found", "text/plain; charset=utf-8")
            return
        self._reply(200, HTML.read_text(encoding="utf-8"), "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/api/solve":
            self._reply(404, "Not found", "text/plain; charset=utf-8")
            return
        length = self.headers.get("Content-Length", "")
        if not length.isdigit() or not 0 < int(length) <= MAX_BODY:
            self._reply(413, '{"error":"Invalid request size"}', "application/json; charset=utf-8")
            return
        try:
            body = json.loads(self.rfile.read(int(length)).decode("utf-8"))
            answer = solve_payload(body)
        except (InvalidScenario, ValueError, TypeError, UnicodeError, ArithmeticError) as exc:
            self._reply(400, json.dumps({"error": str(exc)}, ensure_ascii=False), "application/json; charset=utf-8")
            return
        self._reply(200, json.dumps(answer, ensure_ascii=False), "application/json; charset=utf-8")


if __name__ == "__main__":
    print("Technic local research calculator: http://127.0.0.1:8765")
    HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
