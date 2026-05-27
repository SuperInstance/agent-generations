"""Comprehensive tests for agent_generations."""

import pytest

from agent_generations import Breeding, EvolutionManager, Generation, LineageTree, MutationEngine


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_gen(version="1.0.0", parent=None, fitness=0.5, traits=None, agent_id="hero"):
    return Generation(
        agent_id=agent_id,
        version=version,
        parent_version=parent,
        fitness=fitness,
        traits=traits or {"speed": 10, "strength": 5, "agility": True},
    )


def make_tree(*gens):
    tree = LineageTree("hero")
    for g in gens:
        tree.add(g)
    return tree


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

class TestGeneration:
    def test_creation(self):
        g = make_gen()
        assert g.agent_id == "hero"
        assert g.version == "1.0.0"
        assert g.fitness == 0.5

    def test_invalid_fitness(self):
        with pytest.raises(ValueError):
            make_gen(fitness=1.5)

    def test_invalid_fitness_negative(self):
        with pytest.raises(ValueError):
            make_gen(fitness=-0.1)

    def test_empty_agent_id(self):
        with pytest.raises(ValueError):
            Generation(agent_id="", version="1.0.0")

    def test_empty_version(self):
        with pytest.raises(ValueError):
            Generation(agent_id="hero", version="")

    def test_is_root(self):
        assert make_gen(parent=None).is_root()
        assert not make_gen(parent="0.9.0").is_root()

    def test_trait_access(self):
        g = make_gen(traits={"x": 42})
        assert g.trait("x") == 42
        assert g.trait("missing", "default") == "default"

    def test_set_trait(self):
        g = make_gen()
        g.set_trait("speed", 99)
        assert g.traits["speed"] == 99

    def test_add_milestone(self):
        g = make_gen()
        g.add_milestone("first_blood")
        assert "first_blood" in g.milestones
        g.add_milestone("first_blood")  # no duplicate
        assert len(g.milestones) == 1

    def test_summary(self):
        g = make_gen()
        s = g.summary()
        assert "hero" in s and "1.0.0" in s


# ---------------------------------------------------------------------------
# LineageTree
# ---------------------------------------------------------------------------

class TestLineageTree:
    def test_add_and_get(self):
        g = make_gen()
        tree = make_tree(g)
        assert tree.get("1.0.0") is g

    def test_add_wrong_agent(self):
        g = Generation(agent_id="villain", version="1.0.0")
        with pytest.raises(ValueError, match="agent_id"):
            make_tree(g)

    def test_duplicate_version(self):
        g1 = make_gen(version="1.0.0")
        g2 = make_gen(version="1.0.0")
        tree = LineageTree("hero")
        tree.add(g1)
        with pytest.raises(ValueError, match="already registered"):
            tree.add(g2)

    def test_missing_parent(self):
        g = make_gen(version="2.0.0", parent="1.0.0")
        with pytest.raises(ValueError, match="Parent"):
            make_tree(g)

    def test_root(self):
        g = make_gen(version="1.0.0")
        tree = make_tree(g)
        assert tree.root() is g

    def test_root_empty(self):
        tree = LineageTree("hero")
        assert tree.root() is None

    def test_children_of(self):
        g1 = make_gen(version="1.0.0")
        g2 = make_gen(version="1.1.0", parent="1.0.0")
        g3 = make_gen(version="1.2.0", parent="1.0.0")
        tree = make_tree(g1, g2, g3)
        kids = tree.children_of("1.0.0")
        assert len(kids) == 2
        versions = {k.version for k in kids}
        assert versions == {"1.1.0", "1.2.0"}

    def test_ancestors(self):
        g1 = make_gen(version="1.0.0")
        g2 = make_gen(version="1.1.0", parent="1.0.0")
        g3 = make_gen(version="1.2.0", parent="1.1.0")
        tree = make_tree(g1, g2, g3)
        anc = tree.ancestors("1.2.0")
        assert [g.version for g in anc] == ["1.1.0", "1.0.0"]

    def test_descendants(self):
        g1 = make_gen(version="1.0.0")
        g2 = make_gen(version="1.1.0", parent="1.0.0")
        g3 = make_gen(version="1.2.0", parent="1.1.0")
        tree = make_tree(g1, g2, g3)
        desc = tree.descendants("1.0.0")
        assert len(desc) == 2

    def test_depth(self):
        g1 = make_gen(version="1.0.0")
        g2 = make_gen(version="1.1.0", parent="1.0.0")
        g3 = make_gen(version="1.2.0", parent="1.1.0")
        tree = make_tree(g1, g2, g3)
        assert tree.depth("1.0.0") == 0
        assert tree.depth("1.1.0") == 1
        assert tree.depth("1.2.0") == 2

    def test_len_and_contains(self):
        g = make_gen(version="1.0.0")
        tree = make_tree(g)
        assert len(tree) == 1
        assert "1.0.0" in tree
        assert "9.9.9" not in tree

    def test_all_versions(self):
        g1 = make_gen(version="2.0.0")
        g2 = make_gen(version="1.0.0")
        tree = make_tree(g2, g1)
        assert tree.all_versions() == ["1.0.0", "2.0.0"]


# ---------------------------------------------------------------------------
# MutationEngine
# ---------------------------------------------------------------------------

class TestMutationEngine:
    def test_basic_mutation(self):
        g = make_gen(traits={"speed": 10, "flag": True})
        engine = MutationEngine(mutation_rate=1.0, seed=42)
        child = engine.mutate(g)
        assert child.parent_version == "1.0.0"
        assert child.version == "1.0.1"
        assert child.agent_id == g.agent_id

    def test_zero_rate(self):
        g = make_gen(traits={"speed": 10})
        engine = MutationEngine(mutation_rate=0.0, seed=42)
        child = engine.mutate(g)
        assert child.traits == g.traits

    def test_invalid_rate(self):
        with pytest.raises(ValueError):
            MutationEngine(mutation_rate=1.5)

    def test_version_bump(self):
        from agent_generations.mutation import _bump_patch
        assert _bump_patch("1.2.3") == "1.2.4"
        assert _bump_patch("0.0.0") == "0.0.1"
        assert _bump_patch("weird") == "weird.1"

    def test_custom_mutator(self):
        def flip(traits, key):
            return 999
        engine = MutationEngine(mutation_rate=1.0, trait_mutator=flip, seed=0)
        g = make_gen(traits={"a": 1, "b": 2})
        child = engine.mutate(g)
        assert all(v == 999 for v in child.traits.values())


# ---------------------------------------------------------------------------
# Breeding
# ---------------------------------------------------------------------------

class TestBreeding:
    def test_basic_breed(self):
        a = make_gen(traits={"speed": 10, "power": 5})
        b = make_gen(traits={"speed": 20, "power": 15, "luck": 7})
        breeding = Breeding(crossover_rate=0.5, seed=42)
        child = breeding.breed(a, b)
        assert child.agent_id == "hero"
        assert "luck" in child.traits  # inherited from b
        assert child.fitness == (a.fitness + b.fitness) / 2

    def test_same_agent_required(self):
        a = make_gen(agent_id="hero")
        b = make_gen(agent_id="villain")
        with pytest.raises(ValueError, match="agent_id"):
            Breeding().breed(a, b)

    def test_all_from_a(self):
        a = make_gen(traits={"x": 1})
        b = make_gen(traits={"x": 2})
        child = Breeding(crossover_rate=0.0, seed=0).breed(a, b)
        assert child.traits["x"] == 1

    def test_all_from_b(self):
        a = make_gen(traits={"x": 1})
        b = make_gen(traits={"x": 2})
        child = Breeding(crossover_rate=1.0, seed=0).breed(a, b)
        assert child.traits["x"] == 2

    def test_milestones_merged(self):
        a = make_gen()
        b = make_gen()
        a.add_milestone("m1")
        b.add_milestone("m2")
        child = Breeding().breed(a, b)
        assert "m1" in child.milestones and "m2" in child.milestones


# ---------------------------------------------------------------------------
# EvolutionManager
# ---------------------------------------------------------------------------

class TestEvolutionManager:
    def _setup(self):
        g = make_gen(version="1.0.0", fitness=0.5, traits={"speed": 10})
        tree = make_tree(g)
        mgr = EvolutionManager(tree, fitness_fn=lambda g: g.fitness)
        return mgr, tree

    def test_best(self):
        mgr, tree = self._setup()
        g2 = make_gen(version="1.1.0", parent="1.0.0", fitness=0.9)
        tree.add(g2)
        best = mgr.best(1)
        assert best[0].version == "1.1.0"

    def test_tournament_select(self):
        mgr, tree = self._setup()
        g2 = make_gen(version="1.1.0", parent="1.0.0", fitness=0.9)
        tree.add(g2)
        winner = mgr.tournament_select(k=2)
        assert winner.version in {"1.0.0", "1.1.0"}

    def test_tournament_empty(self):
        tree = LineageTree("hero")
        mgr = EvolutionManager(tree)
        with pytest.raises(ValueError):
            mgr.tournament_select()

    def test_mutate_and_add(self):
        mgr, tree = self._setup()
        parent = tree.get("1.0.0")
        child = mgr.mutate_and_add(parent)
        assert child.parent_version == "1.0.0"
        assert len(tree) == 2

    def test_breed_and_add(self):
        g1 = make_gen(version="1.0.0", fitness=0.6, traits={"x": 1})
        g2 = make_gen(version="1.1.0", parent="1.0.0", fitness=0.8, traits={"x": 2})
        tree = make_tree(g1, g2)
        mgr = EvolutionManager(tree)
        child = mgr.breed_and_add(g1, g2)
        assert len(tree) == 3
        assert child.parent_version == "1.0.0"

    def test_evolve(self):
        mgr, tree = self._setup()
        new = mgr.evolve(steps=5)
        assert len(new) == 5
        assert len(tree) == 6  # original + 5

    def test_evolve_with_seed(self):
        g = make_gen(version="1.0.0", fitness=0.5, traits={"speed": 10})
        tree = make_tree(g)
        mut = MutationEngine(seed=123)
        breed = Breeding(seed=123)
        mgr = EvolutionManager(tree, mutation_engine=mut, breeding=breed)
        new = mgr.evolve(steps=3)
        assert len(new) == 3
