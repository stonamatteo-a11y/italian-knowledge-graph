"""Human-readable ontology nodes for language and humanities.

Generated from the original v0.1 seed without changing identifiers or descriptions.
"""

from .seed_runtime import select_domain_nodes

NODES = select_domain_nodes({
    "lingua_italiana",
    "grammatica_linguistica",
    "letteratura",
    "storia",
    "geografia",
    "filosofia",
    "etica",
})
