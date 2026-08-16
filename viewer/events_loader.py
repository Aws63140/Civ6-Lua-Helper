"""
Event data loader.
"""
import json
import os

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

    def search(self, query: str, event_system: str = "", availability: str = "") -> list:
        """Search events by query + filters.

        Query: space-separated keywords, AND logic.
        Scoring: eventName or eventSystem.eventName full path=100, notes=20.
        """
        pool = self.get_events(event_system, availability)

        if not query:
            return pool

        terms = query.lower().strip().split()
        results = []

        for event in pool:
            event_name = event.get("eventName", "").lower()
            ev_sys = event.get("eventSystem", "").lower()
            full_path = f"{ev_sys}.{event_name}" if ev_sys else event_name
            notes = " ".join(event.get("notes", [])).lower()

            score = 0
            all_match = True
            for term in terms:
                if term in event_name:
                    score += 100
                elif term in full_path:
                    score += 100
                elif term in notes:
                    score += 20
                else:
                    all_match = False
                    break

            if all_match:
                results.append((score, event))

        results.sort(key=lambda x: -x[0])
        return [r[1] for r in results]
