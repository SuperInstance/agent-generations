"""EvolutionManager — fitness-based selection and evolutionary loops."""

from __future__ import annotations

from typing import Callable, List, Optional

from .generation import Generation
from .lineage import LineageTree
from .mutation import MutationEngine
from .breeding import Breeding


FitnessFn = Callable[[Generation], float]


def _identity_fitness(gen: Generation) -> float:
    return gen.fitness


class EvolutionManager:
    """Drive generational evolution for a single agent lineage.

    Parameters:
        tree: The lineage tree to operate on.
        mutation_engine: Engine used to create mutant offspring.
        breeding: Breeding strategy for combining two parents.
        fitness_fn: Callable that evaluates a Generation and returns a float in [0, 1].
    """

    def __init__(
        self,
        tree: LineageTree,
        mutation_engine: Optional[MutationEngine] = None,
        breeding: Optional[Breeding] = None,
        fitness_fn: Optional[FitnessFn] = None,
    ) -> None:
        self.tree = tree
        self.mutation = mutation_engine or MutationEngine()
        self.breeding = breeding or Breeding()
        self.fitness_fn = fitness_fn or _identity_fitness

    # --- selection helpers ---

    def best(self, n: int = 1) -> List[Generation]:
        """Return the top-n generations by fitness."""
        gens = self.tree.all_generations()
        gens.sort(key=lambda g: g.fitness, reverse=True)
        return gens[:n]

    def tournament_select(self, k: int = 3) -> Generation:
        """Pick a random subset of size *k* and return the fittest."""
        import random
        pool = self.tree.all_generations()
        if not pool:
            raise ValueError("No generations to select from")
        candidates = random.sample(pool, min(k, len(pool)))
        return max(candidates, key=lambda g: g.fitness)

    # --- evolutionary steps ---

    def mutate_and_add(self, parent: Generation) -> Generation:
        """Mutate *parent*, evaluate fitness, add to tree, and return child."""
        child = self.mutation.mutate(parent)
        # Ensure unique version in tree
        base_version = child.version
        suffix = 1
        while child.version in self.tree:
            child.version = f"{base_version}-m{suffix}"
            suffix += 1
        child.fitness = self.fitness_fn(child)
        self.tree.add(child)
        return child

    def breed_and_add(
        self, parent_a: Generation, parent_b: Generation
    ) -> Generation:
        """Breed two parents, evaluate fitness, add to tree, return child."""
        child = self.breeding.breed(parent_a, parent_b)
        # Ensure unique version in tree
        base_version = child.version
        suffix = 1
        while child.version in self.tree:
            child.version = f"{base_version}-b{suffix}"
            suffix += 1
        child.fitness = self.fitness_fn(child)
        self.tree.add(child)
        return child

    def evolve(
        self,
        steps: int = 10,
        elite_frac: float = 0.2,
        crossover_prob: float = 0.5,
    ) -> List[Generation]:
        """Run a simple evolutionary loop.

        Each step:
          1. Select elite fraction by fitness.
          2. With *crossover_prob*, breed two random elites; otherwise mutate one.
          3. Add offspring to tree.

        Returns the list of new generations created.
        """
        new_gens: List[Generation] = []
        for _ in range(steps):
            elites = self.best(max(1, int(len(self.tree) * elite_frac)))
            if len(elites) >= 2 and _rng_chance(crossover_prob):
                import random
                a, b = random.sample(elites, 2)
                child = self.breed_and_add(a, b)
            else:
                parent = elites[0]
                child = self.mutate_and_add(parent)
            new_gens.append(child)
        return new_gens


def _rng_chance(p: float) -> bool:
    import random
    return random.random() < p
