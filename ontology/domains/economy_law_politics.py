"""Human-readable ontology branch selection for economy, law and institutions."""

from .seed_runtime import select_domain_nodes

NODES = select_domain_nodes({
    "economia", "finanza", "diritto", "politica_istituzioni", "cittadinanza",
    "lavoro_professioni",
})
