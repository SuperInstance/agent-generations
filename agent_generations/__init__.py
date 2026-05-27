"""agent-generations — Lineage tracking, versioning, and generational evolution of agents."""

from .generation import Generation
from .lineage import LineageTree
from .mutation import MutationEngine
from .evolution import EvolutionManager
from .breeding import Breeding

__all__ = ["Generation", "LineageTree", "MutationEngine", "EvolutionManager", "Breeding"]
__version__ = "0.1.0"
