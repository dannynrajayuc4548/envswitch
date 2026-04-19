"""Watch a profile for changes and emit events."""
from __future__ import annotations
import time
import copy
from typing import Callable, Optional
from envswitch.storage import load_profiles


class ProfileWatcher:
    """Poll a profile for variable changes and call a callback on diff."""

    def __init__(
        self,
        profile_name: str,
        callback: Callable[[dict, dict], None],
        interval: float = 2.0,
    ):
        self.profile_name = profile_name
        self.callback = callback
        self.interval = interval
        self._running = False
        self._last: Optional[dict] = None

    def _current(self) -> Optional[dict]:
        profiles = load_profiles()
        return profiles.get(self.profile_name)

    def check_once(self) -> bool:
        """Check for changes. Returns True if a change was detected."""
        current = self._current()
        if current is None:
            return False
        if self._last is None:
            self._last = copy.deepcopy(current)
            return False
        if current != self._last:
            old = copy.deepcopy(self._last)
            self._last = copy.deepcopy(current)
            self.callback(old, current)
            return True
        return False

    def start(self, max_iterations: Optional[int] = None) -> None:
        """Start polling loop. Runs until stop() is called or max_iterations reached."""
        self._running = True
        self._last = self._current()
        iterations = 0
        while self._running:
            if max_iterations is not None and iterations >= max_iterations:
                break
            time.sleep(self.interval)
            self.check_once()
            iterations += 1

    def stop(self) -> None:
        self._running = False


def format_watch_diff(old: dict, new: dict) -> str:
    """Return a human-readable summary of changes between old and new profile vars."""
    lines = []
    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        if key not in old:
            lines.append(f"  + {key}={new[key]}")
        elif key not in new:
            lines.append(f"  - {key}")
        elif old[key] != new[key]:
            lines.append(f"  ~ {key}: {old[key]!r} -> {new[key]!r}")
    return "\n".join(lines)
