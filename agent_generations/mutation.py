"""MutationEngine — apply random trait changes to generations."""

from __future__ import annotations

import copy
import random
from dataclasses import replace
from typing import Any, Callable, Dict, List, Optional, Tuple

from .generation import Generation


# Type for a mutation function: takes (traits, key) → new value
TraitMutator = Callable[[Dict[str, Any], str], Any]


def _numeric_jitter(traits: Dict[str, Any], key: str) -> Any:
    """Default mutator: add Gaussian noise to numeric, flip booleans, leave rest."""
    val = traits.get(key)
    if isinstance(val, bool):
        return not val
    if isinstance(val, (int, float)):
        sigma = abs(val) * 0.1 + 0.01
        return type(val)(val + random.gauss(0, sigma))
    return val  # non-numeric, non-bool: leave unchanged


class MutationEngine:
    """Apply stochastic trait mutations to a Generation.

    Parameters:
        mutation_rate: Probability each trait key is mutated (0–1).
        trait_mutator: Custom function to compute a new trait value.
    """

    def __init__(
        self,
        mutation_rate: float = 0.3,
        trait_mutator: Optional[TraitMutator] = None,
        seed: Optional[int] = None,
    ) -> None:
        if not 0.0 <= mutation_rate <= 1.0:
            raise ValueError("mutation_rate must be in [0, 1]")
        self.mutation_rate = mutation_rate
        self._mutator = trait_mutator or _numeric_jitter
        self._rng = random.Random(seed)

    def mutate(self, gen: Generation, bump_version: bool = True) -> Generation:
        """Return a new Generation with mutated traits.

        The new generation records *gen.version* as its parent_version.
        """
        new_traits: Dict[str, Any] = copy.deepcopy(gen.traits)
        for key in list(new_traits.keys()):
            if self._rng.random() < self.mutation_rate:
                new_traits[key] = self._mutator(new_traits, key)

        new_version = _bump_patch(gen.version) if bump_version else gen.version

        return Generation(
            agent_id=gen.agent_id,
            version=new_version,
            parent_version=gen.version,
            fitness=gen.fitness,  # fitness may be re-evaluated externally
            traits=new_traits,
            environment=gen.environment,
            training_cycles=gen.training_cycles,
        )


def _bump_patch(version: str) -> str:
    """Increment the patch component of a semver string."""
    parts = version.split(".")
    if len(parts) == 3:
        try:
            parts[2] = str(int(parts[2]) + 1)
            return ".".join(parts)
        except ValueError:
            pass
    return version + ".1"
