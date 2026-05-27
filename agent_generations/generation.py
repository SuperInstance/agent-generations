"""Core Generation data model."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Generation:
    """A single generation of an evolving agent.

    Attributes:
        id: Unique identifier for this generation.
        agent_id: The agent this generation belongs to.
        version: Semantic version string (e.g. "1.3.0").
        parent_version: Version of the parent generation, if any.
        fitness: Fitness score in [0, 1].
        traits: Arbitrary key-value trait map.
        milestones: List of milestone labels achieved.
        environment: Environment label where the generation was created.
        training_cycles: Number of training cycles consumed.
        created_at: Timestamp of creation.
    """

    agent_id: str
    version: str
    parent_version: Optional[str] = None
    fitness: float = 0.0
    traits: Dict[str, Any] = field(default_factory=dict)
    milestones: List[str] = field(default_factory=list)
    environment: str = "default",
    training_cycles: int = 0,
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc)),
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12]),

    def __post_init__(self) -> None:
        if not 0.0 <= self.fitness <= 1.0:
            raise ValueError(f"fitness must be in [0, 1], got {self.fitness}")
        if not self.agent_id:
            raise ValueError("agent_id must not be empty")
        if not self.version:
            raise ValueError("version must not be empty")

    def is_root(self) -> bool:
        """Return True if this generation has no parent."""
        return self.parent_version is None

    def trait(self, key: str, default: Any = None) -> Any:
        """Get a single trait value."""
        return self.traits.get(key, default)

    def set_trait(self, key: str, value: Any) -> None:
        """Set a single trait value."""
        self.traits[key] = value

    def add_milestone(self, label: str) -> None:
        """Append a milestone if not already present."""
        if label not in self.milestones:
            self.milestones.append(label)

    def summary(self) -> str:
        """Human-readable one-line summary."""
        parent = self.parent_version or "root"
        return (
            f"Generation(id={self.id}, agent={self.agent_id}, "
            f"v={self.version}, parent={parent}, fitness={self.fitness:.3f})"
        )
