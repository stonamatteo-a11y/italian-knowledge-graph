"""Human-readable ontology branch selection for formal and natural sciences."""

from .seed_runtime import select_domain_nodes

NODES = select_domain_nodes({
    "matematica", "logica", "statistica_probabilita", "fisica", "chimica",
    "biologia", "astronomia", "scienze_terra",
})
