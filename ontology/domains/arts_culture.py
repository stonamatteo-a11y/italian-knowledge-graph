"""Human-readable ontology branch selection for arts and culture."""

from .seed_runtime import select_domain_nodes

NODES = select_domain_nodes({"arte", "musica", "cinema_spettacolo", "architettura"})
