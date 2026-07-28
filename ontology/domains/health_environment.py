"""Human-readable ontology branch selection for health, environment and safety."""

from .seed_runtime import select_domain_nodes

NODES = select_domain_nodes({"medicina_salute", "ambiente_ecologia", "sicurezza"})
