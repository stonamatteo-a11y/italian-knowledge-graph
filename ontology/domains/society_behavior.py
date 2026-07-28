"""Human-readable ontology branch selection for society and human behavior."""

from .seed_runtime import select_domain_nodes

NODES = select_domain_nodes({
    "psicologia", "sociologia", "antropologia", "religioni", "comunicazione",
    "educazione", "attualita_societa",
})
