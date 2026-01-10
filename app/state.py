from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class InMemoryStore:
    entries: Dict[str, Dict] = field(default_factory=dict)
    attachments_meta: Dict[str, Dict] = field(default_factory=dict)
    attachments_content: Dict[str, bytes] = field(default_factory=dict)
    active_access_tokens: Set[str] = field(default_factory=set)
    refresh_token_index: Dict[str, str] = field(default_factory=dict)
    latest_revision: int = 0

    def next_revision(self) -> int:
        self.latest_revision += 1
        return self.latest_revision
