"""
Event data loader.
"""
import json
import os

from .bool_search import search_entries

_DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "events_enhanced.json"
)


class EventDataLoader:
    """Event data loader.

    Properties:
      metadata: metadata dict
      events: flat list of all event entries
    """

    def __init__(self, data_path=None):
        if data_path is None:
            data_path = _DEFAULT_DATA_PATH
        self.metadata = {}
        self.events = []
        self._load(data_path)

    def _load(self, data_path: str):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.metadata = data.get("metadata", {})
        self.events = data.get("events", [])

    def get_event_systems(self) -> list:
        """Get sorted list of unique event systems."""
        systems = set()
        for e in self.events:
            sys = e.get("eventSystem")
            if sys:
                systems.add(sys)
        return sorted(systems)

    @property
    def total_events(self) -> int:
        return len(self.events)

    @property
    def enriched_count(self) -> int:
        return sum(1 for e in self.events if e.get("enriched"))

    def get_events(self, event_system: str = "", availability: str = "") -> list:
        """Filter events by criteria. Empty string = no filter.

        Only event_system and availability — category filter removed by design.
        """
        if not event_system and not availability:
            return self.events
        results = self.events
        if event_system:
            results = [e for e in results if e.get("eventSystem") == event_system]
        if availability:
            match_set = {availability, "Both"}
            results = [e for e in results if e.get("availability") in match_set]
        return results

    def search(self, query: str, event_system: str = "", availability: str = "") -> tuple:
        """Search events by query + filters.

        Query: boolean expression — AND / OR / NOT (uppercase only),
        quoted phrases, parentheses; space acts as implicit AND
        (see bool_search.py module docstring).
        Scoring: eventName or eventSystem.eventName full path=100, notes=20.
        Returns (results, error); error is not None on syntax error.
        """
        pool = self.get_events(event_system, availability)

        def fields_of(event):
            event_name = event.get("eventName", "").lower()
            ev_sys = event.get("eventSystem", "").lower()
            full_path = f"{ev_sys}.{event_name}" if ev_sys else event_name
            return [
                (event_name, 100),
                (full_path, 100),
                (" ".join(event.get("notes", [])).lower(), 20),
            ]

        return search_entries(pool, query, fields_of)
