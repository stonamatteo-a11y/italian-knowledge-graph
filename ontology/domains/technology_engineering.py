"""Human-readable ontology branch selection for technology and engineering."""

from .seed_runtime import select_domain_nodes

NODES = select_domain_nodes({
    "informatica", "intelligenza_artificiale", "ingegneria", "tecnologia",
    "industria_manifattura", "energia", "trasporti",
})
