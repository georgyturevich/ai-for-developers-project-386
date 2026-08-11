"""Store unit tests: the atomic check-and-insert and the id counter."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from cal_bookings.domain import EventType
from cal_bookings.store import DuplicateSlugError, InMemoryStore, SlotUnavailableError


def event_type(slug: str = "strizhka", duration: int = 60) -> EventType:
    return EventType(id=slug, name=slug, description="x", duration_in_minutes=duration)


def store_with_event_type() -> InMemoryStore:
    store = InMemoryStore()
    store.create_event_type(event_type())
    return store


def start(hour: int) -> datetime:
    return datetime(2026, 8, 12, hour, 0, 0, tzinfo=UTC)


def test_duplicate_slug_raises():
    store = store_with_event_type()
    with pytest.raises(DuplicateSlugError):
        store.create_event_type(event_type())


def test_booking_ids_start_at_one_and_increment():
    store = store_with_event_type()
    first = store.create_booking("strizhka", start(7), 60, "A", "a@example.com", None)
    second = store.create_booking("strizhka", start(8), 60, "B", "b@example.com", None)
    assert first.id == 1
    assert second.id == 2


def test_overlap_raises_even_for_different_event_type():
    store = store_with_event_type()
    store.create_event_type(event_type("masazh", duration=30))
    store.create_booking("strizhka", start(7), 60, "A", "a@example.com", None)
    with pytest.raises(SlotUnavailableError):
        store.create_booking("masazh", start(7), 30, "B", "b@example.com", None)


def test_touching_booking_is_allowed():
    store = store_with_event_type()
    store.create_booking("strizhka", start(7), 60, "A", "a@example.com", None)
    store.create_booking("strizhka", start(8), 60, "B", "b@example.com", None)
    assert len(store.list_bookings()) == 2


def test_occupied_intervals_reflect_bookings():
    store = store_with_event_type()
    store.create_booking("strizhka", start(7), 60, "A", "a@example.com", None)
    intervals = store.occupied_intervals()
    assert len(intervals) == 1
    assert intervals[0].start == start(7)
    assert intervals[0].end == start(8)
