# agent-generations

Track agent versions and evolution across generations.

A Python library for **lineage tracking, versioning, and generational evolution of agents**.

## Installation

```bash
pip install agent-generations
```

## Quick Start

```python
from agent_generations import Generation, LineageTree, MutationEngine, EvolutionManager, Breeding

# Create a root generation
root = Generation(agent_id="my_agent", version="1.0.0", fitness=0.6, traits={"speed": 10, "strength": 5})

# Build a lineage tree
tree = LineageTree("my_agent")
tree.add(root)

# Mutate to create offspring
engine = MutationEngine(mutation_rate=0.3, seed=42)
child = engine.mutate(root)
tree.add(child)

# Breed two parents
parent_b = Generation(agent_id="my_agent", version="1.0.1", parent_version="1.0.0", fitness=0.7, traits={"speed": 12, "strength": 8})
tree.add(parent_b)
baby = Breeding(crossover_rate=0.5).breed(root, parent_b)

# Run an evolutionary loop
mgr = EvolutionManager(tree)
new_generations = mgr.evolve(steps=10)
print(f"Tree now has {len(tree)} generations, best fitness: {mgr.best(1)[0].fitness:.3f}")
```

## Modules

- **`generation`** — `Generation` dataclass with version, parent, traits, fitness
- **`lineage`** — `LineageTree` tracking ancestry and descent
- **`mutation`** — `MutationEngine` applying stochastic trait changes
- **`breeding`** — `Breeding` combining traits from two parent agents
- **`evolution`** — `EvolutionManager` with fitness-based selection and evolutionary loops

## Development

```bash
pip install pytest
pytest tests/ -q
```

## License

MIT

---

Part of the [Cocapn fleet](https://github.com/Lucineer/the-fleet).

<i>Built with [Cocapn](https://github.com/Lucineer/cocapn-ai).</i>

Superinstance & Lucineer (DiGennaro et al.)
