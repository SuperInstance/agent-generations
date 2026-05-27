"""Breeding — combine traits from two parent agents."""

from __future__ import annotations

import copy
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

from .generation import Generation


class Breeding:
    """Produce offspring by combining traits from two parent generations.

    Parameters:
        crossover_rate: Probability of taking a trait from parent_b
                        rather than parent_a for each key.
        seed: Optional RNG seed for reproducibility.
    """

    def __init__(self, crossover_rate: float = 0.5, seed: Optional[int] = None) -> None:
        if not 0.0 <= crossover_rate <= 1.0:
            raise ValueError("crossover_rate must be in [0, 1]")
        self.crossover_rate = crossover_rate
        self._rng = random.Random(seed)

    def breed(
        self,
        parent_a: Generation,
        parent_b: Generation,
        version: Optional[str] = None,
    ) -> Generation:
        """Create a child Generation combining traits from both parents.

        Traits are merged from both parents' keys.  For shared keys the
        value is chosen from parent_a or parent_b according to the
        crossover rate.  The child's fitness is the average of both
        parents (subject to re-evaluation later).
        """
        if parent_a.agent_id != parent_b.agent_id:
            raise ValueError("Parents must belong to the same agent_id for breeding")

        merged_traits: Dict[str, Any] = {}
        all_keys = set(parent_a.traits) | set(parent_b.traits)
        for key in all_keys:
            a_has = key in parent_a.traits
            b_has = key in parent_b.traits
            if a_has and b_has:
                merged_traits[key] = (
                    copy.deepcopy(parent_b.traits[key])
                    if self._rng.random() < self.crossover_rate
                    else copy.deepcopy(parent_a.traits[key])
                )
            elif a_has:
                merged_traits[key] = copy.deepcopy(parent_a.traits[key])
            else:
                merged_traits[key] = copy.deepcopy(parent_b.traits[key])

        child_version = version or _merge_versions(parent_a.version, parent_b.version)
        avg_fitness = (parent_a.fitness + parent_b.fitness) / 2.0

        return Generation(
            agent_id=parent_a.agent_id,
            version=child_version,
            parent_version=parent_a.version,  # primary parent
            fitness=avg_fitness,
            traits=merged_traits,
            milestones=parent_a.milestones + parent_b.milestones,
            environment=parent_a.environment,
            training_cycles=max(parent_a.training_cycles, parent_b.training_cycles),
        )


def _merge_versions(va: str, vb: str) -> str:
    """Derive a child version string from two parent versions."""
    pa = va.split(".")
    pb = vb.split(".")
    parts = []
    for i in range(max(len(pa), len(pb))):
        a = int(pa[i]) if i < len(pa) else 0
        b = int(pb[i]) if i < len(pb) else 0
        parts.append(str(max(a, b)))
    return ".".join(parts)
