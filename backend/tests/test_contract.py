"""Contract conformance: schemathesis in-process against the generated OpenAPI spec.

Every operation from main.tsp is exercised; any response that violates the
generated schema (including an undeclared 5xx) fails the suite. A fresh,
pre-seeded app instance is used for every generated request, so runs are
isolated and the state-dependent success paths are reachable.
"""

from __future__ import annotations

from pathlib import Path

import schemathesis

from cal_bookings import domain
from cal_bookings.app import create_app

SPEC = Path(__file__).parents[2] / "tsp-output" / "@typespec" / "openapi3" / "openapi.yaml"

SEEDED_SLUG = "strizhka"
SEEDED_START = "2026-08-12T07:00:00Z"  # on the 60-minute grid, ahead of any clock

schema = schemathesis.openapi.from_path(str(SPEC))


@schemathesis.hook("before_call")
def _pin_state_dependent_parameters(context, case, kwargs) -> None:
    if case.operation.path == "/event-types/{eventTypeId}/slots":
        case.path_parameters["eventTypeId"] = SEEDED_SLUG
    elif case.operation.path == "/bookings" and case.operation.method == "POST" and isinstance(case.body, dict):
        case.body["eventTypeId"] = SEEDED_SLUG
        case.body["start"] = SEEDED_START


@schema.parametrize()
def test_contract_conformance(case) -> None:
    app = create_app()
    app.state.store.create_event_type(
        domain.EventType(id=SEEDED_SLUG, name="Стрижка", description="Тестовый тип события.", duration_in_minutes=60)
    )
    case.operation.app = app
    case.call_and_validate()
