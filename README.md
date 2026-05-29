# agent-generations — Agent Version Evolution

**Track agent lineage, versioning, and generational evolution. Agents breed, mutate, and evolve.**

## What This Gives You

- **Generation tracking** — version agents with parent-child relationships and generation numbers
- **Lineage trees** — build and query full ancestry trees for any agent
- **Mutation engine** — apply controlled mutations (config changes, capability adjustments) between generations
- **Evolution management** — orchestrate generation transitions with validation and rollback
- **Breeding** — combine traits from two parent agents into offspring configurations

## Quick Start

```bash
pip install agent-generations
```

```python
from agent_generations import Generation, LineageTree, EvolutionManager, Breeding

# Create generations
gen1 = Generation(version=1, agent_id="agent-base", traits={"speed": 0.7, "accuracy": 0.9})
gen2 = Generation(version=2, agent_id="agent-base", traits={"speed": 0.8, "accuracy": 0.9}, parent=gen1)

# Build lineage
tree = LineageTree()
tree.add(gen1)
tree.add(gen2)
ancestry = tree.trace("agent-base")  # [gen2, gen1]

# Breed two agents
offspring = Breeding().breed(
    parent_a={"speed": 0.9, "accuracy": 0.7},
    parent_b={"speed": 0.5, "accuracy": 0.95},
    strategy="average",
)
# {"speed": 0.7, "accuracy": 0.825}

# Manage evolution
manager = EvolutionManager()
manager.register("agent-base", gen1)
evolved = manager.evolve("agent-base", mutations={"speed": +0.1})
```

## API Reference

### `Generation(version, agent_id, traits, parent=None)`
### `LineageTree` — `add(generation)`, `trace(agent_id)`, `roots()`, `descendants(agent_id)`
### `MutationEngine` — `apply(generation, mutations) → Generation`
### `EvolutionManager` — `register(agent_id, generation)`, `evolve(agent_id, mutations)`, `rollback(agent_id, version)`
### `Breeding` — `breed(parent_a, parent_b, strategy) → dict`

## How It Fits

The evolution layer for the [SuperInstance fleet](https://github.com/SuperInstance). Agents improve across generations, with full lineage tracking.

- **[agent-tattoo](https://github.com/SuperInstance/agent-tattoo)** — Tattoos carry forward across generations
- **[agent-resume](https://github.com/SuperInstance/agent-resume)** — Resumes reflect generational capabilities
- **[become-ai](https://github.com/SuperInstance/become-ai)** — Self-evolving agent platform

## Testing

```bash
pytest tests/
```

## Installation

```bash
pip install agent-generations
```

Python 3.10+. MIT license.
