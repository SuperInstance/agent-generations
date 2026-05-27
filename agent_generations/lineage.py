"""LineageTree — track ancestry and descent across generations."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Set

from .generation import Generation


class LineageTree:
    """A directed acyclic graph of Generation nodes keyed by agent_id.

    Each tree is scoped to a single agent_id.  Generations are stored
    once and indexed by version for fast lookup.
    """

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self._by_version: Dict[str, Generation] = {}
        self._children: Dict[str, List[str]] = defaultdict(list)

    # --- mutators ---

    def add(self, gen: Generation) -> None:
        """Register a generation.  Parent must already exist unless this is a root."""
        if gen.agent_id != self.agent_id:
            raise ValueError(
                f"Generation agent_id {gen.agent_id!r} != tree agent_id {self.agent_id!r}"
            )
        if gen.version in self._by_version:
            raise ValueError(f"Version {gen.version!r} already registered")
        if gen.parent_version is not None and gen.parent_version not in self._by_version:
            raise ValueError(f"Parent version {gen.parent_version!r} not found in tree")
        self._by_version[gen.version] = gen
        parent = gen.parent_version
        if parent is not None:
            self._children[parent].append(gen.version)

    # --- queries ---

    def get(self, version: str) -> Optional[Generation]:
        return self._by_version.get(version)

    def root(self) -> Optional[Generation]:
        """Return the root generation (no parent), or None if empty."""
        for g in self._by_version.values():
            if g.is_root():
                return g
        return None

    def children_of(self, version: str) -> List[Generation]:
        """Direct children of *version*."""
        return [self._by_version[v] for v in self._children.get(version, [])]

    def ancestors(self, version: str) -> List[Generation]:
        """All ancestors from parent up to root (inclusive)."""
        chain: List[Generation] = []
        cur = self._by_version.get(version)
        while cur is not None and cur.parent_version is not None:
            cur = self._by_version.get(cur.parent_version)
            if cur is not None:
                chain.append(cur)
        return chain

    def descendants(self, version: str) -> List[Generation]:
        """All descendants (breadth-first) of *version*."""
        result: List[Generation] = []
        queue = list(self._children.get(version, []))
        visited: Set[str] = set()
        while queue:
            v = queue.pop(0)
            if v in visited:
                continue
            visited.add(v)
            gen = self._by_version[v]
            result.append(gen)
            queue.extend(self._children.get(v, []))
        return result

    def all_versions(self) -> List[str]:
        return sorted(self._by_version.keys())

    def all_generations(self) -> List[Generation]:
        return list(self._by_version.values())

    def depth(self, version: str) -> int:
        """Distance from root.  Root has depth 0."""
        return len(self.ancestors(version))

    def __len__(self) -> int:
        return len(self._by_version)

    def __contains__(self, version: str) -> bool:
        return version in self._by_version
